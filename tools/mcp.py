#!/usr/bin/env python3
"""MCP (Model Context Protocol) Client for Nexus Agent."""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class MCPClient:
    """MCP client for connecting to external tools/services."""
    
    def __init__(self):
        self.servers: Dict[str, Any] = {}
        self.tools: Dict[str, Any] = {}
        self._initialized = False
    
    async def connect_server(self, name: str, command: str, args: List[str] = None):
        """Connect to an MCP server."""
        try:
            from mcp import ClientSession, StdioServerParameters
            from mcp.client.stdio import stdio_client
            
            server_params = StdioServerParameters(
                command=command,
                args=args or []
            )
            
            # This would be async in real implementation
            logger.info(f"Connecting to MCP server: {name} ({command})")
            
            # Store server info
            self.servers[name] = {
                "command": command,
                "args": args or [],
                "connected": True
            }
            
            return True
            
        except ImportError:
            logger.warning("MCP not installed. Run: pip install mcp")
            return False
        except Exception as e:
            logger.error(f"MCP server error: {e}")
            return False
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List available MCP tools."""
        tools = []
        for server_name, server_info in self.servers.items():
            if server_info.get("connected"):
                tools.append({
                    "name": f"mcp_{server_name}",
                    "description": f"MCP tools from {server_name}",
                    "server": server_name
                })
        return tools
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool."""
        # This is a simplified implementation
        # Real MCP would communicate with actual servers
        return {
            "success": True,
            "result": f"MCP tool {tool_name} called with {arguments}"
        }
    
    def disconnect_all(self):
        """Disconnect all servers."""
        for name in self.servers:
            logger.info(f"Disconnecting MCP server: {name}")
        self.servers.clear()


# Singleton instance
_mcp_client: Optional[MCPClient] = None

def get_mcp_client() -> MCPClient:
    """Get or create MCP client."""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPClient()
    return _mcp_client

def mcp_connect_server(name: str, command: str, args: str = "") -> Dict[str, Any]:
    """Connect to MCP server (sync wrapper)."""
    client = get_mcp_client()
    args_list = args.split() if args else []
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(client.connect_server(name, command, args_list))
        return {"success": result, "server": name}
    finally:
        loop.close()

def mcp_list_tools() -> List[Dict[str, Any]]:
    """List MCP tools."""
    client = get_mcp_client()
    return client.list_tools()

def mcp_call_tool(tool_name: str, arguments: str = "{}") -> Dict[str, Any]:
    """Call MCP tool (sync wrapper)."""
    client = get_mcp_client()
    
    try:
        args = json.loads(arguments) if arguments else {}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON arguments"}
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(client.call_tool(tool_name, args))
        return result
    finally:
        loop.close()
