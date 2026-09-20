"""
MCP client for InboxHero.
Sends initialize, tools/list and tools/call requests to the MCP server.
"""

import uuid

from mcp_server import MCPServer, ToolRegistry


class MCPClient:
    """Simple client for communicating with the MCP server."""

    def __init__(self, server: MCPServer):
        self.server = server
        self.protocol_version = "2.0"
        self.client_name = "InboxHero MCPClient"

        # Initialize the connection
        request = {
            "jsonrpc": self.protocol_version,
            "id": str(uuid.uuid4()),
            "method": "initialize",
            "params": {"client_name": self.client_name},
        }

        self.init_response = self.server.handle(request)

    def list_tools(self):
        """Get the tools exposed by the server."""
        request = {
            "jsonrpc": self.protocol_version,
            "id": str(uuid.uuid4()),
            "method": "tools/list",
            "params": {},
        }

        response = self.server.handle(request)

        if "error" in response:
            raise RuntimeError(
                f"Error listing tools: {response['error']}"
            )

        return response["result"]

    def call_tool(self, name: str, arguments: dict):
        """Call a tool through the MCP server."""
        request = {
            "jsonrpc": self.protocol_version,
            "id": str(uuid.uuid4()),
            "method": "tools/call",
            "params": {
                "fname": name,
                "arguments": arguments,
            },
        }

        response = self.server.handle(request)

        if "error" in response:
            raise RuntimeError(
                f"Error calling tool {name}: {response['error']}"
            )

        return response["result"]


if __name__ == "__main__":
    registry = ToolRegistry()
    server = MCPServer(registry)
    client = MCPClient(server)

    print("=== Initialize ===")
    print(client.init_response)

    print("\n=== Tools ===")
    for tool in client.list_tools():
        print(tool["name"])

    print("\n=== Inbox Summary ===")
    result = client.call_tool("get_inbox_summary", {})
    print(result)

    print("\n=== Search ===")
    result = client.call_tool(
        "search_messages",
        {"query": "board review"},
    )
    print(result)