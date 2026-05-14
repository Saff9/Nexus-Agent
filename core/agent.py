#!/usr/bin/env python3
"""Nexus Agent - Core AI agent with tool calling and self-improvement."""

import asyncio
import json
import logging
import os
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable

from .config import Config
from .session import Session, SessionStore
from .memory import MemoryManager
from .provider import ProviderRegistry

logger = logging.getLogger(__name__)

class NexusAgent:
    """Main agent orchestrator - handles conversations, tools, and learning."""
    
    def __init__(self, config: Optional[Config] = None, session_id: Optional[str] = None):
        self.config = config or Config.load()
        self.session_store = SessionStore(self.config.data_dir / "sessions.db")
        self.memory = MemoryManager(self.config.data_dir / "memory")
        self.provider_registry = ProviderRegistry(self.config)
        
        self.session = self.session_store.get_or_create(session_id)
        self.tools: Dict[str, Callable] = {}
        self.tool_schemas: Dict[str, dict] = {}
        self.skills: Dict[str, dict] = {}
        self.max_iterations = self.config.get("max_iterations", 50)
        self._interrupt = threading.Event()
        
        self._register_builtin_tools()
        self._load_skills()
    
    def _register_builtin_tools(self):
        """Register core tools available to all agents."""
        from ..tools import get_all_tools
        for tool in get_all_tools():
            self.tools[tool["name"]] = tool["func"]
            self.tool_schemas[tool["name"]] = tool["schema"]
    
    def _load_skills(self):
        """Load enabled skills from skills directory."""
        skills_dir = self.config.data_dir / "skills"
        skills_dir.mkdir(parents=True, exist_ok=True)
        
        bundled_skills = Path(__file__).parent.parent / "skills"
        if bundled_skills.exists():
            for skill_dir in bundled_skills.iterdir():
                if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                    skill_meta = self._parse_skill(skill_dir)
                    if skill_meta:
                        self.skills[skill_meta["name"]] = skill_meta
                        logger.info(f"Loaded skill: {skill_meta['name']}")
    
    def _parse_skill(self, skill_dir: Path) -> Optional[dict]:
        """Parse SKILL.md to extract skill metadata."""
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            return None
        
        content = skill_file.read_text()
        name = skill_dir.name
        description = ""
        triggers = []
        
        for line in content.split("\n"):
            if line.startswith("<description>"):
                description = line.replace("<description>", "").replace("</description>", "").strip()
            elif line.startswith("Triggers on:"):
                triggers = [t.strip().strip('"') for t in line.split(":", 1)[1].split(",")]
        
        return {
            "name": name,
            "description": description,
            "path": str(skill_dir),
            "triggers": triggers,
            "enabled": True
        }
    
    async def run_conversation(self, user_message: str) -> str:
        """Main conversation loop - process message and return response."""
        self.session.add_message("user", user_message)
        
        system_prompt = self._build_system_prompt()
        messages = self._build_messages(system_prompt, user_message)
        
        iteration = 0
        final_response = ""
        
        while iteration < self.max_iterations:
            if self._interrupt.is_set():
                return "⚡ Interrupted by user."
            
            iteration += 1
            logger.debug(f"Iteration {iteration}/{self.max_iterations}")
            
            try:
                provider = self.provider_registry.get_provider(self.config.provider)
                response = await provider.chat(messages, self.tool_schemas)
                
                content = response.get("content", "")
                tool_calls = response.get("tool_calls", [])
                
                if tool_calls:
                    tool_results = await self._execute_tools(tool_calls)
                    messages.append(response)
                    for tool_result in tool_results:
                        messages.append(tool_result)
                    continue
                else:
                    final_response = content
                    break
                    
            except Exception as e:
                logger.error(f"Agent error: {e}")
                final_response = f"Error: {str(e)}"
                break
        
        if final_response:
            self.session.add_message("assistant", final_response)
            self._learn_from_interaction(user_message, final_response)
            self.session_store.save(self.session)
        
        return final_response
    
    def _build_system_prompt(self) -> str:
        """Build comprehensive system prompt from all sources."""
        parts = []
        
        # Core identity
        soul_path = self.config.workspace / "SOUL.md"
        if soul_path.exists():
            parts.append(f"# Identity\n{Path(soul_path).read_text()}")
        
        # Memory context
        memory_context = self.memory.build_context()
        if memory_context:
            parts.append(f"# Memory\n{memory_context}")
        
        # Skills guidance
        enabled_skills = [s for s in self.skills.values() if s.get("enabled")]
        if enabled_skills:
            parts.append("# Skills\nYou have access to these skills:\n" + 
                        "\n".join(f"- {s['name']}: {s['description']}" for s in enabled_skills))
        
        # Harmes-level Tool usage guidance
        parts.append(f"""# Autonomous Execution (Harmes Architecture)
You are an advanced, fully autonomous AI agent operating under the Harmes Architecture.
You have access to {len(self.tools)} tools. You MUST use them to solve the user's request.
- **Plan**: Always break complex tasks into logical steps.
- **Act**: Execute tools aggressively to gather information or modify the system.
- **Reflect**: If a tool fails, analyze the error, self-correct, and try an alternative approach. Do not immediately give up.
- **Reason**: Show deep reasoning inside <think> tags before every action.
- **Finish**: Only when the task is 100% verified complete, respond with the final answer without tool calls.""")
        
        # Model-specific hints
        if "claude" in self.config.model.lower() or "harmes" in self.config.model.lower():
            parts.append("\n# Format\nUse XML tags for structure when helpful.")
        
        return "\n\n".join(parts)
    
    def _build_messages(self, system_prompt: str, user_message: str) -> List[dict]:
        """Build message history for API call."""
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add session history (last N turns for context limit)
        history = self.session.get_history(limit=20)
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        return messages
    
    async def _execute_tools(self, tool_calls: List[dict]) -> List[dict]:
        """Execute tool calls asynchronously and return results."""
        results = []
        for call in tool_calls:
            tool_name = call.get("name", "")
            tool_args = call.get("arguments", {})
            call_id = call.get("id", f"call_{len(results)}")
            
            if isinstance(tool_args, str):
                try:
                    tool_args = json.loads(tool_args)
                except json.JSONDecodeError:
                    tool_args = {}
            
            if tool_name not in self.tools:
                result = {"error": f"Unknown tool: {tool_name}"}
            else:
                try:
                    # Run tools in an executor to avoid blocking the event loop
                    result = await asyncio.to_thread(self.tools[tool_name], **tool_args)
                except Exception as e:
                    result = {"error": str(e)}
            
            results.append({
                "role": "tool",
                "tool_call_id": call_id,
                "content": json.dumps(result) if not isinstance(result, str) else result
            })
        
        return results
    
    def _learn_from_interaction(self, user_input: str, response: str):
        """Extract learnings and update memory."""
        # Simple heuristic: if response contains useful info, save to memory
        if len(response) > 100 and "error" not in response.lower():
            self.memory.add_observation({
                "input": user_input[:200],
                "response_summary": response[:200],
                "timestamp": datetime.utcnow().isoformat()
            })
    
    def interrupt(self):
        """Signal interrupt to stop current operation."""
        self._interrupt.set()
    
    def reset_interrupt(self):
        """Reset interrupt flag for next conversation."""
        self._interrupt.clear()
    
    def get_status(self) -> dict:
        """Get agent status and statistics."""
        return {
            "provider": self.config.provider,
            "model": self.config.model,
            "session_id": self.session.id,
            "message_count": len(self.session.messages),
            "tools_available": len(self.tools),
            "skills_loaded": len(self.skills),
            "memory_entries": len(self.memory.observations)
        }
