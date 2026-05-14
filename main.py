#!/usr/bin/env python3
"""Nexus Agent - Main entry point."""

import sys
import os
from pathlib import Path

# Ensure the package can be imported
sys.path.insert(0, str(Path(__file__).parent))

if __name__ == "__main__":
    # Detect Android environment
    if 'ANDROID_ARGUMENT' in os.environ or 'ANDROID_PRIVATE' in os.environ or hasattr(sys, 'getandroidapilevel'):
        from app import NexusApp
        NexusApp().run()
    else:
        from cli import main as cli_main
        cli_main()
