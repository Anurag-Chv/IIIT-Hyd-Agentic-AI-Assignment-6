def tool(name, description, properties=None, required=None):
    return {
        "name": name,
        "description": description,
        "params": properties or {},
        "required": required or [],
    }


inboxhero_tool_declarations = [
    tool(
        "get_message",
        "Get one message by ID.",
        {"message_id": {"type": "string"}},
        ["message_id"],
    ),
    tool(
        "get_thread",
        "Get all messages in a thread.",
        {"thread_id": {"type": "string"}},
        ["thread_id"],
    ),
    tool(
        "search_messages",
        "Search messages by text.",
        {"query": {"type": "string"}},
        ["query"],
    ),
    tool(
        "get_unread_messages",
        "Get all unread messages.",
    ),
    tool(
        "remember",
        "Store persistent user memory.",
        {
            "key": {"type": "string"},
            "value": {"type": "string"},
            "source": {"type": "string"},
        },
        ["key", "value"],
    ),
    tool(
        "recall",
        "Retrieve stored memory.",
        {"query": {"type": "string"}},
        ["query"],
    ),
    tool(
        "summarize_memory",
        "Summarize persistent memory.",
    ),
]