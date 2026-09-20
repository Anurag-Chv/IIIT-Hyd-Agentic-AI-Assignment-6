"""
InboxHero tools.

These tools provide inbox retrieval, search, persistent memory,
disposition recording, and reversible message actions.

Irreversible actions such as send/delete are intentionally not
implemented here. They will be added behind the safety gate.
"""

import json
from datetime import datetime
from pathlib import Path

import memory
from Common.data import (
    get_message,
    get_thread,
    search_messages,
    get_unread_messages,
    load_inbox,
)


# ------------------------------------------------------------------
# Project paths
# ------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DECISIONS_FILE = PROJECT_ROOT / "decisions.json"
MESSAGE_STATE_FILE = PROJECT_ROOT / "message_state.json"


# ------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------

VALID_DISPOSITIONS = {
    "reply",
    "archive",
    "defer",
    "delegate",
    "escalate",
}


VALID_REVERSIBLE_ACTIONS = {
    "draft",
    "label",
    "archive",
    "defer",
    "delegate",
}


# ------------------------------------------------------------------
# Internal JSON helpers
# ------------------------------------------------------------------

def _load_json(file_path: Path, default):
    """Load JSON from disk or return the supplied default."""
    if not file_path.exists():
        return default

    try:
        with file_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return default


def _save_json(file_path: Path, data):
    """Save JSON to disk."""
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# ------------------------------------------------------------------
# Inbox retrieval tools
# ------------------------------------------------------------------

def list_messages() -> list:
    """
    Return all messages in the inbox.
    """
    return load_inbox()


def get_message_by_id(message_id: str) -> dict:
    """
    Retrieve a single message by ID.
    """
    message = get_message(message_id)

    if message is None:
        return {
            "message": f"No message found with ID {message_id}."
        }

    return message


def get_email_thread(thread_id: str) -> list:
    """
    Retrieve all messages in a thread in timestamp order.
    """
    thread = get_thread(thread_id)

    if not thread:
        return [
            {
                "message": f"No thread found with ID {thread_id}."
            }
        ]

    return thread


def search_inbox(query: str) -> list:
    """
    Search sender, recipient, subject, and body text.
    """
    return search_messages(query)


def list_unread_messages() -> list:
    """
    Return all unread messages.
    """
    return get_unread_messages()


def get_inbox_summary() -> dict:
    """
    Return basic inbox statistics.
    """
    messages = load_inbox()

    unread_count = sum(
        1 for message in messages
        if message.get("unread") is True
    )

    return {
        "total_messages": len(messages),
        "unread_messages": unread_count,
    }


# ------------------------------------------------------------------
# Disposition tools
# ------------------------------------------------------------------

def record_disposition(
    message_id: str,
    disposition: str,
    reason: str,
) -> dict:
    """
    Assign exactly one disposition and reason to a message.

    Existing decisions for the same message are replaced so that
    each message has one current disposition.
    """
    disposition = disposition.lower().strip()

    if disposition not in VALID_DISPOSITIONS:
        return {
            "error": (
                f"Invalid disposition '{disposition}'. "
                f"Allowed values: {sorted(VALID_DISPOSITIONS)}"
            )
        }

    message = get_message(message_id)

    if message is None:
        return {
            "error": f"No message found with ID {message_id}."
        }

    decisions = _load_json(DECISIONS_FILE, {})

    decisions[message_id] = {
        "disposition": disposition,
        "reason": reason.strip(),
        "timestamp": datetime.now().isoformat(),
    }

    _save_json(DECISIONS_FILE, decisions)

    return {
        "message_id": message_id,
        "disposition": disposition,
        "reason": reason.strip(),
    }


def get_disposition(message_id: str) -> dict:
    """
    Retrieve the current disposition for a message.
    """
    decisions = _load_json(DECISIONS_FILE, {})

    decision = decisions.get(message_id)

    if decision is None:
        return {
            "message_id": message_id,
            "disposition": None,
        }

    return {
        "message_id": message_id,
        **decision,
    }


def get_all_dispositions() -> dict:
    """
    Return all recorded message dispositions.
    """
    return _load_json(DECISIONS_FILE, {})


def get_undecided_messages() -> list:
    """
    Return messages that currently have no disposition.
    """
    decisions = _load_json(DECISIONS_FILE, {})
    messages = load_inbox()

    return [
        message["id"]
        for message in messages
        if message["id"] not in decisions
    ]


# ------------------------------------------------------------------
# Reversible actions
# ------------------------------------------------------------------

def apply_reversible_action(
    message_id: str,
    action: str,
    details: dict | None = None,
) -> dict:
    """
    Record/perform a reversible inbox action.

    Supported actions:
        draft
        label
        archive
        defer
        delegate

    No irreversible action is accepted here.
    """
    action = action.lower().strip()

    if action not in VALID_REVERSIBLE_ACTIONS:
        return {
            "error": (
                f"Action '{action}' is not a permitted reversible action."
            )
        }

    message = get_message(message_id)

    if message is None:
        return {
            "error": f"No message found with ID {message_id}."
        }

    state = _load_json(MESSAGE_STATE_FILE, {})
    message_actions = state.setdefault("actions", [])

    action_record = {
        "message_id": message_id,
        "action": action,
        "details": details or {},
        "timestamp": datetime.now().isoformat(),
    }

    message_actions.append(action_record)

    _save_json(MESSAGE_STATE_FILE, state)

    return {
        "status": "completed",
        **action_record,
    }


# ------------------------------------------------------------------
# Persistent memory tools
# ------------------------------------------------------------------

def remember(
    key: str,
    value: str,
    source: str = "manual",
) -> dict:
    """
    Store a persistent preference or fact.
    """
    result = memory.remember(key, value, source)

    return {
        "message": result,
    }


def recall(query: str) -> dict:
    """
    Retrieve a persistent preference or fact.
    """
    result = memory.recall(query)

    if result:
        return {
            "value": result["value"],
            "source": result["source"],
            "timestamp": result["timestamp"],
        }

    return {
        "message": f"No memory found for {query}."
    }


def summarize_memory() -> list:
    """
    Return all persistent memory items in readable form.
    """
    return memory.summarize_memory()