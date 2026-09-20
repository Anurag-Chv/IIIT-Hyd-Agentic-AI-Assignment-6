"""
MCP server for InboxHero.
Supports initialize, tools/list and tools/call.
"""

import sys
import uuid
from pathlib import Path

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
    send,
    delete,
)


class ToolRegistry:
    """Keeps the available InboxHero tools and their metadata."""

    def __init__(self):
        specs = [
            ("list_messages", list_messages, "Return all inbox messages.", {}, []),

            ("get_message", get_message_by_id,
             "Retrieve a message by ID.",
             {"message_id": {"type": "string"}}, ["message_id"]),

            ("get_thread", get_email_thread,
             "Retrieve all messages in a thread.",
             {"thread_id": {"type": "string"}}, ["thread_id"]),

            ("search_messages", search_inbox,
             "Search sender, recipient, subject and body.",
             {"query": {"type": "string"}}, ["query"]),

            ("get_unread_messages", list_unread_messages,
             "Return unread messages.", {}, []),

            ("get_inbox_summary", get_inbox_summary,
             "Return inbox counts.", {}, []),

            ("record_disposition", record_disposition,
             "Assign one disposition and reason to a message.",
             {
                 "message_id": {"type": "string"},
                 "disposition": {"type": "string"},
                 "reason": {"type": "string"},
             },
             ["message_id", "disposition", "reason"]),

            ("get_disposition", get_disposition,
             "Return a message disposition.",
             {"message_id": {"type": "string"}}, ["message_id"]),

            ("get_all_dispositions", get_all_dispositions,
             "Return all message dispositions.", {}, []),

            ("get_undecided_messages", get_undecided_messages,
             "Return messages without a disposition.", {}, []),

            ("apply_reversible_action", apply_reversible_action,
             "Apply a reversible action.",
             {
                 "message_id": {"type": "string"},
                 "action": {"type": "string"},
                 "details": {"type": "object"},
             },
             ["message_id", "action"]),

            ("remember", remember,
             "Store a persistent preference or fact.",
             {
                 "key": {"type": "string"},
                 "value": {"type": "string"},
                 "source": {"type": "string"},
             },
             ["key", "value"]),

            ("recall", recall,
             "Retrieve a saved preference or fact.",
             {"query": {"type": "string"}}, ["query"]),

            ("summarize_memory", summarize_memory,
             "Return stored memory.", {}, []),

            ("send", send,
             "Send a message through the safety gate.",
             {
                 "message_id": {"type": "string"},
                 "to": {"type": "string"},
                 "subject": {"type": "string"},
                 "body": {"type": "string"},
                 "dry_run": {"type": "boolean"},
             },
             ["message_id", "to", "subject", "body"]),

            ("delete", delete,
             "Delete a message through the safety gate.",
             {
                 "message_id": {"type": "string"},
                 "dry_run": {"type": "boolean"},
             },
             ["message_id"]),
        ]

        self.tools = {
            name: {
                "func": func,
                "description": description,
                "params": params,
                "required": required,
            }
            for name, func, description, params, required in specs
        }

    def list_tools(self):
        return [
            {
                "name": name,
                "description": tool["description"],
                "params": tool["params"],
                "required": tool["required"],
            }
            for name, tool in self.tools.items()
        ]

    def call_tool(self, name, arguments):
        if name not in self.tools:
            raise ValueError(f"Unknown tool: {name}")

        if not isinstance(arguments, dict):
            raise ValueError("Tool arguments must be a dictionary.")

        tool = self.tools[name]

        missing = [
            field for field in tool["required"]
            if field not in arguments
        ]

        if missing:
            raise ValueError(
                f"Missing required argument(s): {missing}"
            )

        return tool["func"](**arguments)


class MCPServer:
    """Handles JSON-RPC requests for InboxHero."""

    def __init__(self, registry):
        self.registry = registry
        self.protocol_version = "2.0"
        self.server_name = "InboxHero MCPServer"

    def _response(self, req_id, result=None, error=None):
        response = {
            "jsonrpc": self.protocol_version,
            "id": req_id,
        }

        if error:
            response["error"] = error
        else:
            response["result"] = result

        return response

    def handle(self, request):
        try:
            method = request.get("method")
            req_id = request.get("id", str(uuid.uuid4()))
            params = request.get("params", {})

            if method == "initialize":
                return self._response(
                    req_id,
                    {
                        "server_name": self.server_name,
                        "protocol_version": self.protocol_version,
                    },
                )

            if method == "tools/list":
                return self._response(
                    req_id,
                    self.registry.list_tools(),
                )

            if method == "tools/call":
                name = params.get("fname")
                arguments = params.get("arguments", {})

                if not name:
                    return self._response(
                        req_id,
                        error={
                            "code": -32602,
                            "message": "Missing tool name.",
                        },
                    )

                try:
                    result = self.registry.call_tool(
                        name,
                        arguments,
                    )
                    return self._response(req_id, result)

                except Exception as exc:
                    return self._response(
                        req_id,
                        error={
                            "code": -32001,
                            "message": str(exc),
                        },
                    )

            return self._response(
                req_id,
                error={
                    "code": -32601,
                    "message": f"Unknown method: {method}",
                },
            )

        except Exception as exc:
            return self._response(
                request.get("id"),
                error={
                    "code": -32000,
                    "message": str(exc),
                },
            )


if __name__ == "__main__":
    registry = ToolRegistry()
    server = MCPServer(registry)

    print(server.handle({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {},
    }))

    print(server.handle({
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {},
    }))