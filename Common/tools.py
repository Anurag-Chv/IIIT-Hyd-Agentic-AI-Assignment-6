"""
Tools used by InboxHero.

Inbox tools handle retrieval and search, while actions.py contains
the send/delete operations that are protected by the safety gate.
"""

import json
from datetime import datetime
from pathlib import Path

import memory
from actions import send_message, delete_message
from Common.data import (
    get_message,
    get_thread,
    search_messages,
    get_unread_messages,
    load_inbox,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DECISIONS_FILE = PROJECT_ROOT / "decisions.json"
MESSAGE_STATE_FILE = PROJECT_ROOT / "message_state.json"


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


def _load_json(file_path: Path, default):
    """Load a JSON file or return the default value."""
    if not file_path.exists():
        return default

    try:
        with file_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return default


def _save_json(file_path: Path, data):
    """Save data as JSON."""
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# Inbox retrieval

def list_messages() -> list:
    """Return all inbox messages."""
    return load_inbox()


def get_message_by_id(message_id: str) -> dict:
    """Return one message by ID."""
    message = get_message(message_id)

    if message is None:
        return {"message": f"No message found with ID {message_id}."}

    return message


def get_email_thread(thread_id: str) -> list:
    """Return all messages in a thread."""
    thread = get_thread(thread_id)

    if not thread:
        return [{"message": f"No thread found with ID {thread_id}."}]

    return thread


def search_inbox(query: str) -> list:
    """Search the inbox by sender, recipient, subject or body."""
    return search_messages(query)


def list_unread_messages() -> list:
    """Return unread messages."""
    return get_unread_messages()


def get_inbox_summary() -> dict:
    """Return basic inbox counts."""
    messages = load_inbox()

    unread_count = sum(
        1 for message in messages
        if message.get("unread") is True
    )

    return {
        "total_messages": len(messages),
        "unread_messages": unread_count,
    }


# Dispositions

def record_disposition(
    message_id: str,
    disposition: str,
    reason: str,
) -> dict:
    """Record one disposition and reason for a message."""
    disposition = disposition.lower().strip()

    if disposition not in VALID_DISPOSITIONS:
        return {
            "error": (
                f"Invalid disposition '{disposition}'. "
                f"Allowed values: {sorted(VALID_DISPOSITIONS)}"
            )
        }

    if get_message(message_id) is None:
        return {"error": f"No message found with ID {message_id}."}

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
    """Return the current disposition for a message."""
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
    """Return all recorded dispositions."""
    return _load_json(DECISIONS_FILE, {})


def get_undecided_messages() -> list:
    """Return message IDs that do not have a disposition yet."""
    decisions = _load_json(DECISIONS_FILE, {})

    return [
        message["id"]
        for message in load_inbox()
        if message["id"] not in decisions
    ]


# Reversible actions

def apply_reversible_action(
    message_id: str,
    action: str,
    details: dict | None = None,
) -> dict:
    """
    Record a reversible action.

    Supported actions:
    draft, label, archive, defer and delegate.
    """
    action = action.lower().strip()

    if action not in VALID_REVERSIBLE_ACTIONS:
        return {
            "error": (
                f"Action '{action}' is not supported. "
                f"Allowed values: {sorted(VALID_REVERSIBLE_ACTIONS)}"
            )
        }

    if get_message(message_id) is None:
        return {"error": f"No message found with ID {message_id}."}

    state = _load_json(MESSAGE_STATE_FILE, {})
    actions = state.setdefault("actions", [])

    record = {
        "message_id": message_id,
        "action": action,
        "details": details or {},
        "timestamp": datetime.now().isoformat(),
    }

    actions.append(record)
    _save_json(MESSAGE_STATE_FILE, state)

    return {
        "status": "completed",
        **record,
    }


# Irreversible actions

def send(
    message_id: str,
    to: str,
    subject: str,
    body: str,
    dry_run: bool = False,
) -> dict:
    """Send a message through the safety-gated action."""
    return send_message(
        message_id=message_id,
        to=to,
        subject=subject,
        body=body,
        dry_run=dry_run,
    )


def delete(
    message_id: str,
    dry_run: bool = False,
) -> dict:
    """Delete a message through the safety-gated action."""
    return delete_message(
        message_id=message_id,
        dry_run=dry_run,
    )


# Persistent memory

def remember(
    key: str,
    value: str,
    source: str = "manual",
) -> dict:
    """Store a persistent preference or fact."""
    return {
        "message": memory.remember(key, value, source)
    }


def recall(query: str) -> dict:
    """Retrieve a persistent preference or fact."""
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
    """Return stored memory in readable form."""
    return memory.summarize_memory()