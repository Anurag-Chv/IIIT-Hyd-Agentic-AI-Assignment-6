"""
GateBot exploration script for SkyVault Agent.
Demonstrates calling a tool (find_available_gate) through MCPClient
without importing agent.py or tools.py directly.
"""

import sys
from pathlib import Path

# Add Common/ folder to path
sys.path.insert(0, str(Path(__file__).resolve().parent / "Common"))

from mcp_server import MCPServer, ToolRegistry
from mcp_client import MCPClient


def main():
    # Set up MCP layer
    registry = ToolRegistry()
    server = MCPServer(registry)
    client = MCPClient(server)

    # Call a tool directly through MCPClient
    result = client.call_tool("find_available_gate", {"terminal": "T2"})
    print("GateBot result:", result)


if __name__ == "__main__":
    main()
