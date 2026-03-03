import asyncio
import json
import os
import sys
import subprocess
from typing import Dict, List, Any, Optional

class MCPClient:
    def __init__(self, name: str, command: str, args: List[str], env: Optional[Dict[str, str]] = None):
        self.name = name
        self.command = command
        self.args = args
        self.env = {**os.environ, **(env or {})}
        self.process: Optional[asyncio.subprocess.Process] = None
        self.tools: List[Dict[str, Any]] = []
        self._request_id = 1

    async def start(self):
        print(f"[MCP] Starting server: {self.name}...")
        try:
            self.process = await asyncio.create_subprocess_exec(
                self.command, *self.args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=self.env
            )
            
            # MCP Initialization
            init_res = await self._send_request("initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "Alfred", "version": "1.1.2"}
            })
            
            await self._send_notification("notifications/initialized", {})
            
            # List Tools
            tools_res = await self._send_request("tools/list", {})
            self.tools = tools_res.get("tools", [])
            print(f"[MCP] Server {self.name} ready with {len(self.tools)} tools.")
            
        except Exception as e:
            print(f"[MCP] Failed to start {self.name}: {e}")

    async def _send_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if not self.process:
            return {}
        
        request = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": method,
            "params": params
        }
        self._request_id += 1
        
        line = json.dumps(request) + "\n"
        self.process.stdin.write(line.encode())
        await self.process.stdin.drain()
        
        resp_line = await self.process.stdout.readline()
        if not resp_line:
            return {}
        
        resp = json.loads(resp_line.decode())
        return resp.get("result", {})

    async def _send_notification(self, method: str, params: Dict[str, Any]):
        if not self.process:
            return
        
        notif = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        }
        line = json.dumps(notif) + "\n"
        self.process.stdin.write(line.encode())
        await self.process.stdin.drain()

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        res = await self._send_request("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })
        return res.get("content", "Operation completed via MCP.")

    async def stop(self):
        if self.process:
            self.process.terminate()
            await self.process.wait()

class MCPManager:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.clients: Dict[str, MCPClient] = {}
        self.all_tools: List[Dict[str, Any]] = []

    async def load_servers(self):
        if not os.path.exists(self.config_path):
            return

        with open(self.config_path, "r") as f:
            config = json.load(f)

        servers = config.get("mcpServers", {})
        for name, srv_config in servers.items():
            client = MCPClient(
                name=name,
                command=srv_config.get("command"),
                args=srv_config.get("args", []),
                env=srv_config.get("env")
            )
            await client.start()
            self.clients[name] = client
            
            for tool in client.tools:
                # Add server name as metadata
                tool["_server"] = name
                self.all_tools.append(self._convert_to_gemini(tool))

    def _convert_to_gemini(self, mcp_tool: Dict[str, Any]) -> Dict[str, Any]:
        # Convert MCP tool schema to Gemini function declaration
        return {
            "name": mcp_tool["name"],
            "description": mcp_tool.get("description", ""),
            "parameters": mcp_tool.get("inputSchema", {"type": "OBJECT", "properties": {}}),
            "_mcp_server": mcp_tool["_server"]
        }

    async def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        for client in self.clients.values():
            for tool in client.tools:
                if tool["name"] == tool_name:
                    return await client.call_tool(tool_name, arguments)
        return f"Tool {tool_name} not found in any MCP server."

    async def shutdown(self):
        for client in self.clients.values():
            await client.stop()
