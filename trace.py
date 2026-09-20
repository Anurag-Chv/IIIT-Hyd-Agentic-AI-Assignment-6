"""
Simple event logger for InboxHero.
Events are stored one per line in trace.jsonl.
"""

import json
from datetime import datetime
from pathlib import Path


TRACE_FILE = Path(__file__).resolve().parent / "trace.jsonl"


def log_event(event, **details):
    """
    Add one event to the trace file.
    """
    record = {
        "timestamp": datetime.now().isoformat(),
        "event": event,
        **details,
    }

    with TRACE_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, default=str) + "\n")


def clear_trace():
    """
    Remove the existing trace file.
    Useful when starting a fresh capability run.
    """
    if TRACE_FILE.exists():
        TRACE_FILE.unlink()


def read_trace():
    """
    Read all trace events from the trace file.
    """
    if not TRACE_FILE.exists():
        return []

    events = []

    with TRACE_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if line:
                events.append(json.loads(line))

    return events