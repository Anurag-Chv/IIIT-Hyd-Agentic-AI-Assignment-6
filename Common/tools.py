import json
from datetime import datetime
from pathlib import Path

import memory
from actions import send_message, delete_message
from Common.data import (
    load_inbox,
    get_message,
    get_thread,
    search_messages,
    get_unread_messages,
)

ROOT = Path(__file__).resolve().parents[1]
DECISIONS_FILE = ROOT / "decisions.json"
MESSAGE_STATE_FILE = ROOT / "message_state.json"

VALID_DISPOSITIONS = {"reply", "archive", "defer", "delegate", "escalate"}
VALID_ACTIONS = {"draft", "label", "archive", "defer", "delegate"}


def _load(path, default):
    if not path.exists():
        return default
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return default


def _save(path, data):
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def list_messages():
    return load_inbox()


def get_message_by_id(message_id):
    message = get_message(message_id)
    return message or {"message": f"No message found with ID {message_id}."}


def get_email_thread(thread_id):
    thread = get_thread(thread_id)
    return thread or [{"message": f"No thread found with ID {thread_id}."}]


def search_inbox(query):
    return search_messages(query)


def list_unread_messages():
    return get_unread_messages()


def get_inbox_summary():
    messages = load_inbox()
    return {
        "total_messages": len(messages),
        "unread_messages": sum(m.get("unread") is True for m in messages),
    }


def record_disposition(message_id, disposition, reason):
    disposition = disposition.lower().strip()

    if disposition not in VALID_DISPOSITIONS:
        return {"error": f"Invalid disposition: {disposition}"}

    if get_message(message_id) is None:
        return {"error": f"No message found with ID {message_id}."}

    decisions = _load(DECISIONS_FILE, {})
    decisions[message_id] = {
        "disposition": disposition,
        "reason": reason.strip(),
        "timestamp": datetime.now().isoformat(),
    }
    _save(DECISIONS_FILE, decisions)

    return {
        "message_id": message_id,
        "disposition": disposition,
        "reason": reason.strip(),
    }


def get_disposition(message_id):
    decisions = _load(DECISIONS_FILE, {})
    return decisions.get(
        message_id,
        {"message_id": message_id, "disposition": None},
    )


def get_all_dispositions():
    return _load(DECISIONS_FILE, {})


def get_undecided_messages():
    decisions = _load(DECISIONS_FILE, {})
    return [
        m["id"]
        for m in load_inbox()
        if m["id"] not in decisions
    ]


def apply_reversible_action(message_id, action, details=None):
    action = action.lower().strip()

    if action not in VALID_ACTIONS:
        return {"error": f"Unsupported action: {action}"}

    if get_message(message_id) is None:
        return {"error": f"No message found with ID {message_id}."}

    state = _load(MESSAGE_STATE_FILE, {"actions": []})
    record = {
        "message_id": message_id,
        "action": action,
        "details": details or {},
        "timestamp": datetime.now().isoformat(),
    }

    state.setdefault("actions", []).append(record)
    _save(MESSAGE_STATE_FILE, state)

    return {"status": "completed", **record}


def send(message_id, to, subject, body, dry_run=False):
    return send_message(message_id, to, subject, body, dry_run)


def delete(message_id, dry_run=False):
    return delete_message(message_id, dry_run)


def remember(key, value, source="manual"):
    return {"message": memory.remember(key, value, source)}


def recall(query):
    result = memory.recall(query)
    return result or {"message": f"No memory found for {query}."}


def summarize_memory():
    return memory.summarize_memory()