#!/usr/bin/env python3
"""Nexus Agent Tools - Built-in capabilities."""

import json
import os
import subprocess
import sys
import logging
from pathlib import Path
from typing import Any, Callable, Dict, List

logger = logging.getLogger(__name__)

def get_all_tools() -> List[Dict[str, Any]]:
    """Get all registered tools."""
    tools = [
        # File operations
        {
            "name": "read_file",
            "func": read_file,
            "schema": {
                "name": "read_file",
                "description": "Read contents of a file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path to read"}
                    },
                    "required": ["path"]
                }
            }
        },
        {
            "name": "write_file",
            "func": write_file,
            "schema": {
                "name": "write_file",
                "description": "Write content to a file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path"},
                        "content": {"type": "string", "description": "Content to write"}
                    },
                    "required": ["path", "content"]
                }
            }
        },
        {
            "name": "search_files",
            "func": search_files,
            "schema": {
                "name": "search_files",
                "description": "Search for files matching a pattern",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pattern": {"type": "string", "description": "Search pattern (glob)"},
                        "path": {"type": "string", "description": "Base directory"}
                    },
                    "required": ["pattern"]
                }
            }
        },
        {
            "name": "list_directory",
            "func": list_directory,
            "schema": {
                "name": "list_directory",
                "description": "List directory contents",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Directory path"}
                    },
                    "required": ["path"]
                }
            }
        },
        # Terminal/Shell
        {
            "name": "run_command",
            "func": run_command,
            "schema": {
                "name": "run_command",
                "description": "Execute a shell command",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "Command to execute"},
                        "timeout": {"type": "integer", "description": "Timeout in seconds"}
                    },
                    "required": ["command"]
                }
            }
        },
        # Web
        {
            "name": "web_search",
            "func": web_search,
            "schema": {
                "name": "web_search",
                "description": "Search the web",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"}
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "name": "web_fetch",
            "func": web_fetch,
            "schema": {
                "name": "web_fetch",
                "description": "Fetch content from a URL",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL to fetch"}
                    },
                    "required": ["url"]
                }
            }
        },
        # System
        {
            "name": "get_env",
            "func": get_env,
            "schema": {
                "name": "get_env",
                "description": "Get environment variable",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Environment variable name"}
                    },
                    "required": ["name"]
                }
            }
        },
        # Browser tools
        {
            "name": "browser_navigate",
            "func": browser_navigate,
            "schema": {
                "name": "browser_navigate",
                "description": "Navigate browser to URL",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL to visit"}
                    },
                    "required": ["url"]
                }
            }
        },
        {
            "name": "browser_screenshot",
            "func": browser_screenshot,
            "schema": {
                "name": "browser_screenshot",
                "description": "Take browser screenshot",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Screenshot path"}
                    },
                    "required": []
                }
            }
        },
        {
            "name": "browser_click",
            "func": browser_click,
            "schema": {
                "name": "browser_click",
                "description": "Click element in browser",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "selector": {"type": "string", "description": "CSS selector"}
                    },
                    "required": ["selector"]
                }
            }
        },
        {
            "name": "browser_fill",
            "func": browser_fill,
            "schema": {
                "name": "browser_fill",
                "description": "Fill input field",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "selector": {"type": "string", "description": "CSS selector"},
                        "value": {"type": "string", "description": "Value to fill"}
                    },
                    "required": ["selector", "value"]
                }
            }
        },
        {
            "name": "browser_content",
            "func": browser_content,
            "schema": {
                "name": "browser_content",
                "description": "Get page content",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        },
        # MCP
        {
            "name": "mcp_connect_server",
            "func": mcp_connect_server,
            "schema": {
                "name": "mcp_connect_server",
                "description": "Connect to MCP server",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Server name"},
                        "command": {"type": "string", "description": "Server command"},
                        "args": {"type": "string", "description": "Arguments"}
                    },
                    "required": ["name", "command"]
                }
            }
        },
        {
            "name": "mcp_call_tool",
            "func": mcp_call_tool,
            "schema": {
                "name": "mcp_call_tool",
                "description": "Call MCP tool",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "tool_name": {"type": "string", "description": "Tool name"},
                        "arguments": {"type": "string", "description": "JSON arguments"}
                    },
                    "required": ["tool_name"]
                }
            }
        },
    ]
    
    # Import browser tools
    try:
        from . import browser
        tools.extend([
            {"name": "browser_evaluate", "func": browser.browser_evaluate, "schema": {
                "name": "browser_evaluate", "description": "Execute JavaScript",
                "parameters": {"type": "object", "properties": {
                    "javascript": {"type": "string", "description": "JS code"}
                }, "required": ["javascript"]}}
            },
        ])
    except Exception as e:
        logger.warning(f"Browser tools not loaded: {e}")
    
    # Import MCP tools
    try:
        from . import mcp
        tools.extend([
            {"name": "mcp_list_tools", "func": mcp.mcp_list_tools, "schema": {
                "name": "mcp_list_tools", "description": "List MCP tools",
                "parameters": {"type": "object", "properties": {}, "required": []}}
            },
        ])
    except Exception as e:
        logger.warning(f"MCP tools not loaded: {e}")
    
    return tools


# Tool implementations

def read_file(path: str) -> str:
    """Read file contents."""
    try:
        return Path(path).expanduser().read_text()
    except Exception as e:
        return f"Error: {str(e)}"

def write_file(path: str, content: str) -> str:
    """Write content to file."""
    try:
        p = Path(path).expanduser()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
        return f"Successfully wrote {len(content)} bytes to {path}"
    except Exception as e:
        return f"Error: {str(e)}"

def search_files(pattern: str, path: str = ".") -> List[str]:
    """Search for files matching pattern."""
    try:
        import glob
        base = Path(path).expanduser()
        matches = glob.glob(str(base / pattern), recursive=True)
        return matches[:50]  # Limit results
    except Exception as e:
        return [f"Error: {str(e)}"]

def run_command(command: str, timeout: int = 60) -> Dict[str, Any]:
    """Execute shell command."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.getcwd()
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"error": f"Command timed out after {timeout}s"}
    except Exception as e:
        return {"error": str(e)}

def web_search(query: str) -> str:
    """Search the web using DuckDuckGo HTML."""
    try:
        import httpx
        # Use DuckDuckGo HTML interface (no API key needed)
        url = f"https://html.duckduckgo.com/html/?q={query}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = httpx.get(url, headers=headers, timeout=10)
        
        # Parse simple results
        results = []
        for line in response.text.split('\n'):
            if 'result__a' in line:
                start = line.find('href="') + 6
                if start > 5:
                    end = line.find('"', start)
                    if end > start:
                        results.append(line[start:end])
                        if len(results) >= 5:
                            break
        
        return "\n".join(results) if results else "No results found"
    except Exception as e:
        return f"Search error: {str(e)}"

def web_fetch(url: str) -> str:
    """Fetch and extract content from URL."""
    try:
        import httpx
        response = httpx.get(url, timeout=15)
        response.raise_for_status()
        
        # Simple HTML to text extraction
        html = response.text
        # Remove scripts and styles
        for tag in ['script', 'style', 'nav', 'header', 'footer']:
            while f'<{tag}' in html.lower():
                start = html.lower().find(f'<{tag}')
                end = html.lower().find(f'</{tag}>') + len(f'</{tag}>')
                if start >= 0 and end > start:
                    html = html[:start] + html[end:]
        
        # Extract text between tags
        text = ' '.join(html.split())
        return text[:3000]  # Limit length
    except Exception as e:
        return f"Fetch error: {str(e)}"

def get_env(name: str) -> str:
    """Get environment variable."""
    return os.environ.get(name, f"(not set)")

def list_directory(path: str = ".") -> List[str]:
    """List directory contents."""
    try:
        p = Path(path).expanduser()
        if not p.exists():
            return [f"Error: Path does not exist"]
        
        items = []
        for item in p.iterdir():
            prefix = "[DIR] " if item.is_dir() else ""
            items.append(f"{prefix}{item.name}")
        return sorted(items)
    except Exception as e:
        return [f"Error: {str(e)}"]
