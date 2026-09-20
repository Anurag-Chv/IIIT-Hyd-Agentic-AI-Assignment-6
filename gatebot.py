from mcp_server import MCPServer, ToolRegistry
from mcp_client import MCPClient


def main():
    client = MCPClient(MCPServer(ToolRegistry()))

    print("=== InboxHero MCP Demo ===")

    print("\nSearch:")
    print(client.call_tool(
        "search_messages",
        {"query": "board review"},
    ))

    print("\nThread:")
    print(client.call_tool(
        "get_thread",
        {"thread_id": "t-launch"},
    ))


if __name__ == "__main__":
    main()