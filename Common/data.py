"""
Data access layer for InboxHero.

Loads the supplied inbox.json file and provides helper functions
for retrieving messages and thread context.
"""

import json
from pathlib import Path


# Project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Supplied Assignment 6 inbox
INBOX_FILE = PROJECT_ROOT / "inbox.json"


def load_inbox():
    """
    Load all inbox messages from inbox.json.

    Returns:
        list: List of message dictionaries.
    """
    if not INBOX_FILE.exists():
        raise FileNotFoundError(
            f"Inbox file not found: {INBOX_FILE}"
        )

    try:
        with INBOX_FILE.open("r", encoding="utf-8") as f:
            messages = json.load(f)

    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Invalid JSON in inbox file: {INBOX_FILE}"
        ) from exc

    if not isinstance(messages, list):
        raise ValueError(
            "inbox.json must contain a JSON list of messages."
        )

    return messages


def get_message(message_id):
    """
    Return a message by its ID.

    Returns:
        dict | None
    """
    for message in load_inbox():
        if message.get("id") == message_id:
            return message

    return None


def get_thread(thread_id):
    """
    Return all messages belonging to a thread.

    Messages are returned in timestamp order.
    """
    messages = [
        message
        for message in load_inbox()
        if message.get("thread_id") == thread_id
    ]

    return sorted(
        messages,
        key=lambda message: message.get("timestamp", "")
    )


def get_thread_for_message(message_id):
    """
    Return the complete thread containing a message.
    """
    message = get_message(message_id)

    if message is None:
        return []

    return get_thread(message.get("thread_id"))


def search_messages(query):
    """
    Search messages by matching the query against:
    sender, recipient, subject and body.

    Returns:
        list: Matching messages.
    """
    query = query.lower().strip()

    if not query:
        return []

    results = []

    for message in load_inbox():
        searchable_text = " ".join(
            [
                str(message.get("from", "")),
                str(message.get("to", "")),
                str(message.get("subject", "")),
                str(message.get("body", "")),
            ]
        ).lower()

        if query in searchable_text:
            results.append(message)

    return results


def get_unread_messages():
    """
    Return all currently unread messages.
    """
    return [
        message
        for message in load_inbox()
        if message.get("unread") is True
    ]


def get_message_count():
    """
    Return the total number of messages in the inbox.
    """
    return len(load_inbox())