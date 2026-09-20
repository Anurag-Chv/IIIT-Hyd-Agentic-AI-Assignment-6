import json
from datetime import datetime
from pathlib import Path

TRACE_FILE = Path(__file__).resolve().parent / "trace.jsonl"


def log_event(event, **details):
    record = {
        "timestamp": datetime.now().isoformat(),
        "event": event,
        **details,
    }

    with TRACE_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, default=str) + "\n")


def clear_trace():
    if TRACE_FILE.exists():
        TRACE_FILE.unlink()


def read_trace():
    if not TRACE_FILE.exists():
        return []

    events = []

    with TRACE_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                events.append(json.loads(line))

    return events