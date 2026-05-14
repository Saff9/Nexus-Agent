#!/usr/bin/env python3
"""Nexus Agent CLI - Interactive terminal interface."""

import asyncio
import os
import sys
import signal
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from core import NexusAgent, Config
from core.config import Config as ConfigClass

class CLI:
    """Interactive CLI for Nexus Agent."""
    
    BANNER = """
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║   ⚡  N E X U S   A G E N T                           ║
║       The Self-Improving AI Assistant                 ║
║                                                       ║
║   Type /help for commands, /quit to exit              ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
"""
    
    def __init__(self):
        self.config = ConfigClass.load()
        self.agent: Optional[NexusAgent] = None
        self.running = True
        self._setup_interrupt_handler()
    
    def _setup_interrupt_handler(self):
        """Handle Ctrl+C gracefully."""
        def handler(sig, frame):
            print("\n⚡ Interrupted. Type /quit to exit.")
            if self.agent:
                self.agent.interrupt()
        signal.signal(signal.SIGINT, handler)
    
    def _init_agent(self):
        """Initialize the agent."""
        if not self.agent:
            print("⚡ Initializing Nexus Agent...")
            self.agent = NexusAgent(self.config)
            status = self.agent.get_status()
            print(f"✓ Provider: {status['provider']}")
            print(f"✓ Model: {status['model']}")
            print(f"✓ Tools: {status['tools_available']}")
            print(f"✓ Skills: {status['skills_loaded']}")
            print()
    
    def _handle_command(self, command: str) -> bool:
        """Handle slash commands. Returns False if should exit."""
        parts = command.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        if cmd in ['/quit', '/exit', '/q']:
            print("⚡ Goodbye!")
            return False
        
        elif cmd == '/help':
            self._show_help()
        
        elif cmd == '/status':
            self._show_status()
        
        elif cmd == '/model':
            self._change_model(args)
        
        elif cmd == '/new':
            self._new_session()
        
        elif cmd == '/clear':
            os.system('cls' if os.name == 'nt' else 'clear')
        
        elif cmd == '/config':
            self._show_config()
        
        elif cmd == '/tools':
            self._list_tools()
        
        elif cmd == '/skills':
            self._list_skills()
        
        elif cmd == '/memory':
            self._show_memory()
        
        else:
            print(f"Unknown command: {cmd}. Type /help for commands.")
        
        return True
    
    def _show_help(self):
        """Show help message."""
        print("""
╭────────────────────────────────────────────────────────────╮
│  ⚡ NEXUS AGENT COMMANDS                                   │
├────────────────────────────────────────────────────────────┤
│  /help          Show this help message                     │
│  /status        Show agent status                          │
│  /model [name]  Change AI model                            │
│  /new           Start new conversation session             │
│  /clear         Clear screen                               │
│  /config        Show current configuration                 │
│  /tools         List available tools                       │
│  /skills        List loaded skills                         │
│  /memory        Show memory summary                        │
│  /quit          Exit Nexus Agent                           │
╰────────────────────────────────────────────────────────────╯
""")
    
    def _show_status(self):
        """Show agent status."""
        self._init_agent()
        status = self.agent.get_status()
        print(f"""
⚡ Agent Status
─────────────────────────────────
Provider:     {status['provider']}
Model:        {status['model']}
Session:      {status['session_id'][:8]}...
Messages:     {status['message_count']}
Tools:        {status['tools_available']}
Skills:       {status['skills_loaded']}
Memory:       {status['memory_entries']} entries
""")
    
    def _change_model(self, args: str):
        """Change the model."""
        if not args:
            print(f"Current model: {self.config.model}")
            print("Usage: /model <provider:model>")
            print("Examples:")
            print("  /model openai:gpt-4o-mini")
            print("  /model anthropic:claude-sonnet-4-20250514")
            print("  /model ollama:llama3.1")
            return
        
        self.config.set("model", args)
        self.agent = None  # Reset agent to apply new model
        print(f"✓ Model changed to: {args}")
    
    def _new_session(self):
        """Start a new session."""
        self.agent = NexusAgent(self.config)
        print("✓ New session started")
    
    def _show_config(self):
        """Show current configuration."""
        print("\n⚡ Configuration")
        print("─────────────────────────────────")
        for key, value in self.config.all().items():
            print(f"  {key}: {value}")
        print()
    
    def _list_tools(self):
        """List available tools."""
        self._init_agent()
        print("\n⚡ Available Tools")
        print("─────────────────────────────────")
        for name in sorted(self.agent.tools.keys()):
            print(f"  • {name}")
        print()
    
    def _list_skills(self):
        """List loaded skills."""
        self._init_agent()
        print("\n⚡ Loaded Skills")
        print("─────────────────────────────────")
        for name, skill in self.agent.skills.items():
            status = "✓" if skill.get('enabled') else "○"
            print(f"  {status} {name}: {skill.get('description', 'No description')}")
        print()
    
    def _show_memory(self):
        """Show memory summary."""
        self._init_agent()
        print("\n⚡ Memory Summary")
        print("─────────────────────────────────")
        print(f"Observations: {len(self.agent.memory.observations)}")
        print(f"Learnings: {len(self.agent.memory.learnings)}")
        if self.agent.memory.user_profile:
            print(f"User profile: {len(self.agent.memory.user_profile)} fields")
        print()
    
    async def run(self):
        """Main CLI loop."""
        print(self.BANNER)
        
        # Lazy init agent on first message
        while self.running:
            try:
                user_input = input("\n❯ ").strip()
                
                if not user_input:
                    continue
                
                if user_input.startswith('/'):
                    if not self._handle_command(user_input):
                        break
                    continue
                
                # Initialize agent if not already done
                self._init_agent()
                
                # Reset interrupt for new message
                self.agent.reset_interrupt()
                
                # Process message
                print("⚡ Thinking...", end="\r")
                response = await self.agent.run_conversation(user_input)
                print(" " * 20, end="\r")  # Clear "Thinking..."
                
                print(f"\n⚡ {response}\n")
                
            except EOFError:
                break
            except KeyboardInterrupt:
                print("\n⚡ Press /quit to exit")
            except Exception as e:
                print(f"⚡ Error: {e}")


def main():
    """CLI entry point."""
    cli = CLI()
    try:
        asyncio.run(cli.run())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
