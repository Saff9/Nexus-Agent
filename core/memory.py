#!/usr/bin/env python3
"""Memory management for persistent knowledge across sessions."""

import json
import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

class MemoryManager:
    """Manages persistent memory including observations, user profile, and learnings."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.memory_file = self.data_dir / "MEMORY.md"
        self.user_file = self.data_dir / "USER.md"
        self.observations_file = self.data_dir / "observations.json"
        
        self.observations: List[Dict[str, Any]] = []
        self.user_profile: Dict[str, Any] = {}
        self.learnings: List[str] = []
        
        self._load()
    
    def _load(self):
        """Load all memory files."""
        # Load observations
        if self.observations_file.exists():
            try:
                with open(self.observations_file, 'r') as f:
                    self.observations = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load observations: {e}")
                self.observations = []
        
        # Load user profile
        if self.user_file.exists():
            try:
                content = self.user_file.read_text()
                self.user_profile = self._parse_user_md(content)
            except Exception as e:
                logger.error(f"Failed to load user profile: {e}")
        
        # Load MEMORY.md learnings
        if self.memory_file.exists():
            try:
                content = self.memory_file.read_text()
                self.learnings = self._extract_learnings(content)
            except Exception as e:
                logger.error(f"Failed to load learnings: {e}")
    
    def _parse_user_md(self, content: str) -> Dict[str, Any]:
        """Parse USER.md markdown into structured data."""
        profile = {}
        current_section = None
        
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('## '):
                current_section = line[3:].strip()
                profile[current_section] = []
            elif line.startswith('- **') and current_section:
                # Parse key-value pairs like "- **Name:** John"
                try:
                    key, value = line[4:].split('**:', 1)
                    profile[key.strip()] = value.strip()
                except ValueError:
                    logger.warning(f"Malformed user profile line: {line}")
            elif line and current_section and line.startswith('-'):
                profile[current_section].append(line[1:].strip())
        
        return profile
    
    def _extract_learnings(self, content: str) -> List[str]:
        """Extract learning entries from MEMORY.md."""
        learnings = []
        in_learnings = False
        
        for line in content.split('\n'):
            if '## Learnings' in line or '## To Remember' in line:
                in_learnings = True
                continue
            if in_learnings and line.startswith('-'):
                learnings.append(line[1:].strip())
            elif in_learnings and line.startswith('##'):
                break
        
        return learnings
    
    def add_observation(self, observation: Dict[str, Any]):
        """Add a new observation to memory."""
        self.observations.append({
            **observation,
            "id": len(self.observations) + 1,
            "created_at": datetime.utcnow().isoformat()
        })
        # Keep only recent observations (last 500)
        if len(self.observations) > 500:
            self.observations = self.observations[-500:]
        self._save_observations()
    
    def add_learning(self, learning: str):
        """Add a new learning entry."""
        if learning not in self.learnings:
            self.learnings.append(learning)
            self._update_memory_md()
    
    def update_user_profile(self, updates: Dict[str, Any]):
        """Update user profile with new information."""
        self.user_profile.update(updates)
        self._update_user_md()
    
    def build_context(self) -> str:
        """Build memory context for system prompt."""
        parts = []
        
        # User profile summary
        if self.user_profile:
            profile_parts = []
            for key, value in self.user_profile.items():
                if isinstance(value, list):
                    profile_parts.append(f"{key}: {', '.join(value)}")
                else:
                    profile_parts.append(f"{key}: {value}")
            if profile_parts:
                parts.append("User Profile:\n" + "\n".join(f"- {p}" for p in profile_parts))
        
        # Recent learnings
        if self.learnings:
            parts.append("Key Learnings:\n" + "\n".join(f"- {l}" for l in self.learnings[-10:]))
        
        # Recent observations summary
        if self.observations:
            recent = self.observations[-5:]
            parts.append("Recent Context:\n" + "\n".join(
                f"- {o.get('input', '')[:100]}" for o in recent if o.get('input')
            ))
        
        return "\n\n".join(parts) if parts else ""
    
    def search_observations(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search observations by keyword."""
        query_lower = query.lower()
        matches = []
        
        for obs in reversed(self.observations):
            content = f"{obs.get('input', '')} {obs.get('response_summary', '')}".lower()
            if query_lower in content:
                matches.append(obs)
                if len(matches) >= limit:
                    break
        
        return matches
    
    def _save_observations(self):
        """Save observations to file."""
        try:
            with open(self.observations_file, 'w') as f:
                json.dump(self.observations, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving observations: {e}")
    
    def _update_memory_md(self):
        """Update MEMORY.md file with current learnings."""
        content = f"""# Memory — Nexus Agent

## Learnings
"""
        for learning in self.learnings:
            content += f"- {learning}\n"
        
        content += f"""
## Observations
Total: {len(self.observations)} entries

Last updated: {datetime.utcnow().isoformat()}
"""
        try:
            self.memory_file.write_text(content)
        except Exception as e:
            logger.error(f"Error updating MEMORY.md: {e}")
    
    def _update_user_md(self):
        """Update USER.md file with current profile."""
        content = "# USER.md - About Your Human\n\n"
        
        for key, value in self.user_profile.items():
            if isinstance(value, list):
                content += f"## {key}\n"
                for item in value:
                    content += f"- {item}\n"
                content += "\n"
            else:
                content += f"- **{key}:** {value}\n"
        
        try:
            self.user_file.write_text(content)
        except Exception as e:
            logger.error(f"Error updating USER.md: {e}")
    
    def export_memory(self) -> Dict[str, Any]:
        """Export all memory data."""
        return {
            "user_profile": self.user_profile,
            "learnings": self.learnings,
            "observations": self.observations,
            "exported_at": datetime.utcnow().isoformat()
        }
