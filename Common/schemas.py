"""
Tool schemas for InboxHero.

These are provider-independent tool definitions used by the MCP
tool registry and agent. They are plain Python dictionaries rather
than Gemini-specific FunctionDeclaration objects.
"""


def _make_tool(
    name: str,
    description: str,
    params: dict,
    required: list,
) -> dict:
    """
    Create a consistent provider-independent tool definition.
    """
    return {
        "name": name,
        "description": description,
        "params": params,
        "required": required,
    }


# ------------------------------------------------------------------
# Inbox data tools
# ------------------------------------------------------------------

get_message_tool = _make_tool(
    name="get_message",
    description=(
        "Retrieve a specific email by its message ID. "
        "Use this when the exact contents of a known message are needed."
    ),
    params={
        "message_id": {
            "type": "string",
            "description": "Message ID, for example 'm003'.",
        }
    },
    required=["message_id"],
)


get_thread_tool = _make_tool(
    name="get_thread",
    description=(
        "Retrieve all messages belonging to an email thread. "
        "Use this when earlier messages are needed to understand context "
        "or ground a reply."
    ),
    params={
        "thread_id": {
            "type": "string",
            "description": "Thread ID, for example 't-launch'.",
        }
    },
    required=["thread_id"],
)


search_messages_tool = _make_tool(
    name="search_messages",
    description=(
        "Search the inbox using sender, recipient, subject, and body text. "
        "Use this for cross-thread information retrieval."
    ),
    params={
        "query": {
            "type": "string",
            "description": "Text to search for in the inbox.",
        }
    },
    required=["query"],
)


get_unread_messages_tool = _make_tool(
    name="get_unread_messages",
    description=(
        "Return all messages currently marked unread."
    ),
    params={},
    required=[],
)


# ------------------------------------------------------------------
# Persistent memory tools
# ------------------------------------------------------------------

remember_tool = _make_tool(
    name="remember",
    description=(
        "Store a user preference or fact persistently so it survives "
        "process exit and restart."
    ),
    params={
        "key": {
            "type": "string",
            "description": "Unique memory key.",
        },
        "value": {
            "type": "string",
            "description": "Preference or fact to remember.",
        },
        "source": {
            "type": "string",
            "description": "Source of the remembered information.",
        },
    },
    required=["key", "value"],
)


recall_tool = _make_tool(
    name="recall",
    description=(
        "Retrieve a previously stored preference or fact from persistent memory."
    ),
    params={
        "query": {
            "type": "string",
            "description": "Memory key to retrieve.",
        }
    },
    required=["query"],
)


summarize_memory_tool = _make_tool(
    name="summarize_memory",
    description=(
        "Return a human-readable summary of all persistent memory items."
    ),
    params={},
    required=[],
)


# ------------------------------------------------------------------
# Static tool catalog
#
# Runtime discovery is still performed through MCPClient.list_tools().
# This catalog provides a provider-independent reference for the
# MCP/tool implementation.
# ------------------------------------------------------------------

inboxhero_tool_declarations = [
    get_message_tool,
    get_thread_tool,
    search_messages_tool,
    get_unread_messages_tool,
    remember_tool,
    recall_tool,
    summarize_memory_tool,
]