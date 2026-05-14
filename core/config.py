#!/usr/bin/env python3
"""Configuration management for Nexus Agent."""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

class Config:
    """Centralized configuration management."""
    
    DEFAULTS = {
        "provider": "openrouter",
        "model": "google/gemini-2.0-flash-001",
        "max_iterations": 50,
        "temperature": 0.7,
        "max_tokens": 4096,
        "workspace": "~/nexus-workspace",
        "data_dir": "~/.nexus",
        "log_level": "INFO",
        "auto_approve_tools": ["read_file", "search_files", "web_search"],
    }
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path.home() / ".nexus" / "config.json"
        self._config: Dict[str, Any] = {}
        self._load()
    
    @property
    def data_dir(self) -> Path:
        """Get data directory, creating if needed."""
        path = Path(self.get("data_dir")).expanduser()
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def workspace(self) -> Path:
        """Get workspace directory, creating if needed."""
        path = Path(self.get("workspace")).expanduser()
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def provider(self) -> str:
        return self.get("provider")
    
    @property
    def model(self) -> str:
        return self.get("model")
    
    def _load(self) -> bool:
        """Load configuration from file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    self._config = json.load(f)
                return True
            except Exception as e:
                print(f"Warning: Could not load config: {e}")
        self._config = self.DEFAULTS.copy()
        return False
    
    def save(self) -> bool:
        """Save configuration to file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self._config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        if key in self._config:
            return self._config[key]
        return self.DEFAULTS.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self._config[key] = value
        self.save()
    
    def all(self) -> Dict[str, Any]:
        """Get all configuration values (merged with defaults)."""
        merged = self.DEFAULTS.copy()
        merged.update(self._config)
        return merged
    
    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> 'Config':
        """Factory method to load config."""
        config = cls(config_path)
        config._load()
        return config
