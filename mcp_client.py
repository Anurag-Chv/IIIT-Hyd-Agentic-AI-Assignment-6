import uuid

from mcp_server import MCPServer, ToolRegistry


class MCPClient:
    def __init__(self, server: MCPServer):
        self.server = server
        self.protocol_version = "2.0"

        self.init_response = self._send(
            "initialize",
            {"client_name": "InboxHero MCPClient"},
        )

    def _send(self, method, params=None):
        request = {
            "jsonrpc": self.protocol_version,
            "id": str(uuid.uuid4()),
            "method": method,
            "params": params or {},
        }

        response = self.server.handle(request)

        if "error" in response:
            raise RuntimeError(response["error"])

        return response["result"]

    def list_tools(self):
        return self._send("tools/list")

    def call_tool(self, name, arguments=None):
        return self._send(
            "tools/call",
            {
                "fname": name,
                "arguments": arguments or {},
            },
        )


if __name__ == "__main__":
    client = MCPClient(MCPServer(ToolRegistry()))

    print("=== Initialize ===")
    print(client.init_response)

    print("\n=== Tools ===")
    for item in client.list_tools():
        print(item["name"])

    print("\n=== Inbox Summary ===")
    print(client.call_tool("get_inbox_summary"))

    print("\n=== Search ===")
    print(client.call_tool(
        "search_messages",
        {"query": "board review"},
    ))