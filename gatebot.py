"""
InboxBot exploration script for InboxHero.

Demonstrates that InboxHero tools can be called through the MCP
client without importing agent.py directly.
"""

import sys
from pathlib import Path

# Add project root and Common/ to the Python path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "Common"))

from mcp_server import MCPServer, ToolRegistry
from mcp_client import MCPClient


def main():
    """
    Run a small MCP smoke test for InboxHero tools.
    """

    registry = ToolRegistry()
    server = MCPServer(registry)
    client = MCPClient(server)

    print("=== InboxBot MCP Demo ===")

    # Test inbox search
    result = client.call_tool(
        "search_messages",
        {"query": "board review"},
    )
    print("\nSearch result:")
    print(result)

    # Test thread retrieval
    result = client.call_tool(
        "get_thread",
        {"thread_id": "t-launch"},
    )
    print("\nThread result:")
    print(result)


if __name__ == "__main__":
    main()