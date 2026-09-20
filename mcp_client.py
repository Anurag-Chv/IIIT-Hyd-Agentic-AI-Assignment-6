"""
MCP Client for SkyVault Agent.
Implements JSON-RPC style requests to the MCPServer:
- initialize
- tools/list
- tools/call

The client sends correctly-shaped dictionaries and returns parsed results.
"""

import uuid
from mcp_server import MCPServer, ToolRegistry


class MCPClient:
    """
    MCPClient communicates with MCPServer using JSON-RPC messages.
    """

    def __init__(self, server: MCPServer):
        self.server = server
        self.protocol_version = "2.0"
        self.client_name = "SkyVault MCPClient"

        # Perform handshake at startup
        init_req = {
            "jsonrpc": self.protocol_version,
            "id": str(uuid.uuid4()),
            "method": "initialize",
            "params": {"client_name": self.client_name},
        }
        self.init_response = self.server.handle(init_req)

    def list_tools(self):
        """Request the list of tools from the server."""
        req = {
            "jsonrpc": self.protocol_version,
            "id": str(uuid.uuid4()),
            "method": "tools/list",
            "params": {},
        }
        resp = self.server.handle(req)
        if "error" in resp:
            raise RuntimeError(f"Error listing tools: {resp['error']}")
        return resp["result"]

    def call_tool(self, name: str, arguments: dict):
        """Call a tool by name with arguments."""
        req = {
            "jsonrpc": self.protocol_version,
            "id": str(uuid.uuid4()),
            "method": "tools/call",
            "params": {"fname": name, "arguments": arguments},
        }
        resp = self.server.handle(req)
        if "error" in resp:
            raise RuntimeError(f"Error calling tool {name}: {resp['error']}")
        return resp["result"]


# Demo run (only executes if mcp_client.py is run directly)
if __name__ == "__main__":
    registry = ToolRegistry()
    server = MCPServer(registry)
    client = MCPClient(server)

    print("=== Initialize ===")
    print(client.init_response)

    print("\n=== Tools List ===")
    tools = client.list_tools()
    for t in tools:
        print(t)

    print("\n=== Call Tool (find_available_gate) ===")
    result = client.call_tool("find_available_gate", {"terminal": "T2"})
    print(result)

    print("\n=== Call Tool (remember + recall) ===")
    client.call_tool("remember", {"key": "preferred_terminal", "value": "T2", "source": "demo"})
    recall_result = client.call_tool("recall", {"query": "preferred_terminal"})
    print(recall_result)
