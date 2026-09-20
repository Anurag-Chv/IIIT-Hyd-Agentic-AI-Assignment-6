"""
MCP Server for SkyVault Agent (Assignment 5).
Implements JSON-RPC style message lifecycle by hand:
- initialize
- tools/list
- tools/call

Wraps all tools (including memory) behind a protocol boundary.
"""

import uuid
from tools import (
    find_available_gate,
    get_flight_status,
    get_weather,
    lookup_aircraft,
    maintenance_history,
    search_passenger,
    remember,
    recall,
)


class ToolRegistry:
    """
    Registry of all available tools.
    Each tool is described with name, description, parameters, and required fields.
    """

    def __init__(self):
        self.tools = {
            "get_flight_status": {
                "func": get_flight_status,
                "description": "Retrieve the current status of a flight.",
                "params": {"flight_number": {"type": "STRING"}},
                "required": ["flight_number"],
            },
            "search_passenger": {
                "func": search_passenger,
                "description": "Look up a passenger's booking details.",
                "params": {"name": {"type": "STRING"}},
                "required": ["name"],
            },
            "maintenance_history": {
                "func": maintenance_history,
                "description": "Get maintenance and inspection records for an aircraft.",
                "params": {"tail_number": {"type": "STRING"}},
                "required": ["tail_number"],
            },
            "find_available_gate": {
                "func": find_available_gate,
                "description": "Find an available boarding gate at a terminal.",
                "params": {"terminal": {"type": "STRING"}},
                "required": ["terminal"],
            },
            "get_weather": {
                "func": get_weather,
                "description": "Get current weather conditions at an airport.",
                "params": {"airport": {"type": "STRING"}},
                "required": ["airport"],
            },
            "lookup_aircraft": {
                "func": lookup_aircraft,
                "description": "Look up technical specifications for an aircraft type.",
                "params": {"aircraft_type": {"type": "STRING"}},
                "required": ["aircraft_type"],
            },
            "remember": {
                "func": remember,
                "description": "Store a fact persistently in memory_store.json.",
                "params": {
                    "key": {"type": "STRING"},
                    "value": {"type": "STRING"},
                    "source": {"type": "STRING"},
                },
                "required": ["key", "value"],
            },
            "recall": {
                "func": recall,
                "description": "Retrieve a fact from persistent memory_store.json.",
                "params": {"query": {"type": "STRING"}},
                "required": ["query"],
            },
        }

    def list_tools(self):
        """Return metadata for all tools."""
        return [
            {
                "name": name,
                "description": meta["description"],
                "params": meta["params"],
                "required": meta["required"],
            }
            for name, meta in self.tools.items()
        ]

    def call_tool(self, name, arguments):
        """Execute a tool by name with given arguments."""
        if name not in self.tools:
            raise ValueError(f"Unknown tool: {name}")
        func = self.tools[name]["func"]
        return func(**arguments)


class MCPServer:
    """
    MCPServer handles JSON-RPC requests and returns responses.
    """

    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        self.protocol_version = "2.0"
        self.server_name = "SkyVault MCPServer"

    def _make_response(self, req_id, result=None, error=None):
        resp = {"jsonrpc": self.protocol_version, "id": req_id}
        if error:
            resp["error"] = error
        else:
            resp["result"] = result
        return resp

    def handle(self, request: dict) -> dict:
        """Process a JSON-RPC request and return a response."""
        try:
            method = request.get("method")
            req_id = request.get("id", str(uuid.uuid4()))
            params = request.get("params", {})

            if method == "initialize":
                return self._make_response(
                    req_id,
                    result={
                        "server_name": self.server_name,
                        "protocol_version": self.protocol_version,
                    },
                )

            elif method == "tools/list":
                return self._make_response(req_id, result=self.registry.list_tools())

            elif method == "tools/call":
                fname = params.get("fname")
                arguments = params.get("arguments", {})
                try:
                    result = self.registry.call_tool(fname, arguments)
                    return self._make_response(req_id, result=result)
                except Exception as e:
                    return self._make_response(
                        req_id,
                        error={"code": -32001, "message": str(e)},
                    )

            else:
                return self._make_response(
                    req_id,
                    error={"code": -32601, "message": f"Unknown method: {method}"},
                )

        except Exception as e:
            return self._make_response(
                request.get("id", None),
                error={"code": -32000, "message": f"Server error: {str(e)}"},
            )


# Demo run (only executes if mcp_server.py is run directly)
if __name__ == "__main__":
    registry = ToolRegistry()
    server = MCPServer(registry)

    # Example initialize
    init_req = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
    print(server.handle(init_req))

    # Example tools/list
    list_req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
    print(server.handle(list_req))

    # Example tools/call
    call_req = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {"fname": "find_available_gate", "arguments": {"terminal": "T2"}},
    }
    print(server.handle(call_req))
