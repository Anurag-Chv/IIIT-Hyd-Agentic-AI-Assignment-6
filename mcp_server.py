"""
MCP Server for InboxHero.

Implements the hand-built JSON-RPC style protocol used in Assignment 5:
- initialize
- tools/list
- tools/call

All InboxHero tools are exposed behind the MCP protocol boundary.
"""

import sys
import uuid
from pathlib import Path

# Ensure project root and Common/ are available
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "Common"))

from tools import (
    list_messages,
    get_message_by_id,
    get_email_thread,
    search_inbox,
    list_unread_messages,
    get_inbox_summary,
    record_disposition,
    get_disposition,
    get_all_dispositions,
    get_undecided_messages,
    apply_reversible_action,
    remember,
    recall,
    summarize_memory,
)


class ToolRegistry:
    """
    Registry of InboxHero tools.

    Each entry contains:
    - function
    - description
    - parameters
    - required parameters
    """

    def __init__(self):
        self.tools = {
            "list_messages": {
                "func": list_messages,
                "description": "Return all messages in the inbox.",
                "params": {},
                "required": [],
            },
            "get_message": {
                "func": get_message_by_id,
                "description": "Retrieve a specific email by message ID.",
                "params": {
                    "message_id": {
                        "type": "string",
                        "description": "Message ID, for example m003.",
                    }
                },
                "required": ["message_id"],
            },
            "get_thread": {
                "func": get_email_thread,
                "description": (
                    "Retrieve all messages belonging to an email thread "
                    "in timestamp order."
                ),
                "params": {
                    "thread_id": {
                        "type": "string",
                        "description": "Thread ID, for example t-launch.",
                    }
                },
                "required": ["thread_id"],
            },
            "search_messages": {
                "func": search_inbox,
                "description": (
                    "Search sender, recipient, subject and body text "
                    "across the inbox."
                ),
                "params": {
                    "query": {
                        "type": "string",
                        "description": "Text to search for.",
                    }
                },
                "required": ["query"],
            },
            "get_unread_messages": {
                "func": list_unread_messages,
                "description": "Return all unread messages.",
                "params": {},
                "required": [],
            },
            "get_inbox_summary": {
                "func": get_inbox_summary,
                "description": "Return basic inbox statistics.",
                "params": {},
                "required": [],
            },
            "record_disposition": {
                "func": record_disposition,
                "description": (
                    "Assign exactly one disposition and reason to a message."
                ),
                "params": {
                    "message_id": {
                        "type": "string",
                        "description": "Message ID.",
                    },
                    "disposition": {
                        "type": "string",
                        "description": (
                            "One of reply, archive, defer, "
                            "delegate or escalate."
                        ),
                    },
                    "reason": {
                        "type": "string",
                        "description": "One-line reason for the disposition.",
                    },
                },
                "required": ["message_id", "disposition", "reason"],
            },
            "get_disposition": {
                "func": get_disposition,
                "description": "Return the current disposition of a message.",
                "params": {
                    "message_id": {
                        "type": "string",
                        "description": "Message ID.",
                    }
                },
                "required": ["message_id"],
            },
            "get_all_dispositions": {
                "func": get_all_dispositions,
                "description": "Return all recorded message dispositions.",
                "params": {},
                "required": [],
            },
            "get_undecided_messages": {
                "func": get_undecided_messages,
                "description": (
                    "Return messages that do not yet have a disposition."
                ),
                "params": {},
                "required": [],
            },
            "apply_reversible_action": {
                "func": apply_reversible_action,
                "description": (
                    "Perform a reversible inbox action such as draft, "
                    "label, archive, defer or delegate."
                ),
                "params": {
                    "message_id": {
                        "type": "string",
                        "description": "Message ID.",
                    },
                    "action": {
                        "type": "string",
                        "description": (
                            "Reversible action: draft, label, archive, "
                            "defer or delegate."
                        ),
                    },
                    "details": {
                        "type": "object",
                        "description": "Optional action details.",
                    },
                },
                "required": ["message_id", "action"],
            },
            "remember": {
                "func": remember,
                "description": (
                    "Store a user preference or fact persistently."
                ),
                "params": {
                    "key": {
                        "type": "string",
                        "description": "Memory key.",
                    },
                    "value": {
                        "type": "string",
                        "description": "Preference or fact to remember.",
                    },
                    "source": {
                        "type": "string",
                        "description": "Source of the information.",
                    },
                },
                "required": ["key", "value"],
            },
            "recall": {
                "func": recall,
                "description": (
                    "Retrieve a previously stored preference or fact."
                ),
                "params": {
                    "query": {
                        "type": "string",
                        "description": "Memory key to retrieve.",
                    }
                },
                "required": ["query"],
            },
            "summarize_memory": {
                "func": summarize_memory,
                "description": "Return all stored persistent memories.",
                "params": {},
                "required": [],
            },
        }

    def list_tools(self):
        """
        Return tool metadata without exposing Python function objects.
        """
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
        """
        Execute a registered tool after validating its name and arguments.
        """
        if name not in self.tools:
            raise ValueError(f"Unknown tool: {name}")

        if not isinstance(arguments, dict):
            raise ValueError("Tool arguments must be a dictionary.")

        meta = self.tools[name]

        missing = [
            field
            for field in meta["required"]
            if field not in arguments
        ]

        if missing:
            raise ValueError(
                f"Missing required argument(s) for {name}: {missing}"
            )

        return meta["func"](**arguments)


class MCPServer:
    """
    Handle JSON-RPC style MCP requests.
    """

    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        self.protocol_version = "2.0"
        self.server_name = "InboxHero MCPServer"

    def _make_response(self, req_id, result=None, error=None):
        """
        Construct a JSON-RPC response.
        """
        response = {
            "jsonrpc": self.protocol_version,
            "id": req_id,
        }

        if error is not None:
            response["error"] = error
        else:
            response["result"] = result

        return response

    def handle(self, request: dict) -> dict:
        """
        Process one JSON-RPC request.
        """
        try:
            if not isinstance(request, dict):
                return self._make_response(
                    None,
                    error={
                        "code": -32600,
                        "message": "Request must be a JSON object.",
                    },
                )

            method = request.get("method")
            req_id = request.get("id", str(uuid.uuid4()))
            params = request.get("params", {})

            if not isinstance(params, dict):
                return self._make_response(
                    req_id,
                    error={
                        "code": -32602,
                        "message": "Request params must be an object.",
                    },
                )

            # ------------------------------------------------------
            # Initialize
            # ------------------------------------------------------

            if method == "initialize":
                return self._make_response(
                    req_id,
                    result={
                        "server_name": self.server_name,
                        "protocol_version": self.protocol_version,
                    },
                )

            # ------------------------------------------------------
            # List tools
            # ------------------------------------------------------

            if method == "tools/list":
                return self._make_response(
                    req_id,
                    result=self.registry.list_tools(),
                )

            # ------------------------------------------------------
            # Call tool
            # ------------------------------------------------------

            if method == "tools/call":
                tool_name = params.get("fname")
                arguments = params.get("arguments", {})

                if not tool_name:
                    return self._make_response(
                        req_id,
                        error={
                            "code": -32602,
                            "message": "Missing tool name.",
                        },
                    )

                try:
                    result = self.registry.call_tool(
                        tool_name,
                        arguments,
                    )

                    return self._make_response(
                        req_id,
                        result=result,
                    )

                except Exception as exc:
                    return self._make_response(
                        req_id,
                        error={
                            "code": -32001,
                            "message": str(exc),
                        },
                    )

            # ------------------------------------------------------
            # Unknown method
            # ------------------------------------------------------

            return self._make_response(
                req_id,
                error={
                    "code": -32601,
                    "message": f"Unknown method: {method}",
                },
            )

        except Exception as exc:
            return self._make_response(
                request.get("id") if isinstance(request, dict) else None,
                error={
                    "code": -32000,
                    "message": f"Server error: {exc}",
                },
            )


if __name__ == "__main__":
    registry = ToolRegistry()
    server = MCPServer(registry)

    print("=== InboxHero MCP Server Demo ===")

    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {},
    }

    print("\nInitialize:")
    print(server.handle(init_request))

    list_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {},
    }

    print("\nTools:")
    print(server.handle(list_request))

    call_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "fname": "get_inbox_summary",
            "arguments": {},
        },
    }

    print("\nTool call:")
    print(server.handle(call_request))