"""
Actions that can change the inbox state.

Send and delete are irreversible, so both go through the safety gate.
"""

import json
from datetime import datetime
from pathlib import Path

from Common.data import get_message
from safety import require_approval
from trace import log_event


PROJECT_ROOT = Path(__file__).resolve().parent
OUTBOX_DIR = PROJECT_ROOT / "outbox"
DELETED_FILE = PROJECT_ROOT / "deleted_messages.json"


def _load_deleted():
    """Load the list of deleted message IDs."""
    if not DELETED_FILE.exists():
        return []

    try:
        with DELETED_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def _save_deleted(message_ids):
    """Save deleted message IDs."""
    with DELETED_FILE.open("w", encoding="utf-8") as f:
        json.dump(message_ids, f, indent=2)


def send_message(
    message_id: str,
    to: str,
    subject: str,
    body: str,
    dry_run: bool = False,
) -> dict:
    """
    Send a message after passing the safety gate.

    In this assignment, sending means writing one JSON file
    to the outbox directory.
    """
    message = get_message(message_id)

    if message is None:
        return {
            "error": f"No message found with ID {message_id}."
        }

    details = {
        "to": to,
        "subject": subject,
        "body": body,
    }

    approved = require_approval(
        "send",
        message_id,
        details,
        dry_run=dry_run,
    )

    if not approved:
        return {
            "status": "not_sent",
            "message_id": message_id,
            "reason": "Not approved or dry-run mode.",
        }

    OUTBOX_DIR.mkdir(exist_ok=True)

    output_file = OUTBOX_DIR / f"{message_id}.json"

    sent_message = {
        "message_id": message_id,
        "to": to,
        "subject": subject,
        "body": body,
        "timestamp": datetime.now().isoformat(),
    }

    with output_file.open("w", encoding="utf-8") as f:
        json.dump(sent_message, f, indent=2)

    log_event(
        "send",
        message_id=message_id,
        output_file=str(output_file),
        status="sent",
    )

    return {
        "status": "sent",
        "message_id": message_id,
        "outbox_file": str(output_file),
    }


def delete_message(
    message_id: str,
    dry_run: bool = False,
) -> dict:
    """
    Delete a message after passing the safety gate.

    The original inbox.json is kept unchanged. Deleted IDs are
    recorded separately so the supplied source data remains intact.
    """
    message = get_message(message_id)

    if message is None:
        return {
            "error": f"No message found with ID {message_id}."
        }

    approved = require_approval(
        "delete",
        message_id,
        {
            "subject": message.get("subject", ""),
        },
        dry_run=dry_run,
    )

    if not approved:
        return {
            "status": "not_deleted",
            "message_id": message_id,
            "reason": "Not approved or dry-run mode.",
        }

    deleted_ids = _load_deleted()

    if message_id not in deleted_ids:
        deleted_ids.append(message_id)

    _save_deleted(deleted_ids)

    log_event(
        "delete",
        message_id=message_id,
        status="deleted",
    )

    return {
        "status": "deleted",
        "message_id": message_id,
    }