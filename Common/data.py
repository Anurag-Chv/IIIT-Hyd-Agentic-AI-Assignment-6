import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INBOX_FILE = PROJECT_ROOT / "inbox.json"


def load_inbox():
    if not INBOX_FILE.exists():
        raise FileNotFoundError(f"Inbox file not found: {INBOX_FILE}")

    try:
        with INBOX_FILE.open("r", encoding="utf-8") as f:
            messages = json.load(f)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON in {INBOX_FILE}") from exc

    if not isinstance(messages, list):
        raise ValueError("inbox.json must contain a JSON list of messages.")

    return messages


def get_message(message_id):
    for message in load_inbox():
        if message.get("id") == message_id:
            return message

    return None


def get_thread(thread_id):
    messages = [
        message
        for message in load_inbox()
        if message.get("thread_id") == thread_id
    ]

    return sorted(
        messages,
        key=lambda message: message.get("timestamp", ""),
    )


def get_thread_for_message(message_id):
    message = get_message(message_id)

    if message is None:
        return []

    return get_thread(message.get("thread_id"))


def search_messages(query):
    query = query.lower().strip()

    if not query:
        return []

    results = []

    for message in load_inbox():
        text = " ".join(
            str(message.get(field, ""))
            for field in ("from", "to", "subject", "body")
        ).lower()

        if query in text:
            results.append(message)

    return results


def get_unread_messages():
    return [
        message
        for message in load_inbox()
        if message.get("unread") is True
    ]


def get_message_count():
    return len(load_inbox())