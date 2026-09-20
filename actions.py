import json
from datetime import datetime
from pathlib import Path

from Common.data import get_message
from safety import require_approval
from trace import log_event


ROOT = Path(__file__).resolve().parent
OUTBOX_DIR = ROOT / "outbox"
DELETED_FILE = ROOT / "deleted_messages.json"


def _load_deleted():
    if not DELETED_FILE.exists():
        return []

    try:
        with DELETED_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def _save_deleted(ids):
    with DELETED_FILE.open("w", encoding="utf-8") as f:
        json.dump(ids, f, indent=2)


def send_message(message_id, to, subject, body, dry_run=False):
    if get_message(message_id) is None:
        return {"error": f"No message found with ID {message_id}."}

    details = {
        "to": to,
        "subject": subject,
        "body": body,
    }

    if not require_approval(
        "send",
        message_id,
        details,
        dry_run=dry_run,
    ):
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


def delete_message(message_id, dry_run=False):
    message = get_message(message_id)

    if message is None:
        return {"error": f"No message found with ID {message_id}."}

    details = {"subject": message.get("subject", "")}

    if not require_approval(
        "delete",
        message_id,
        details,
        dry_run=dry_run,
    ):
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