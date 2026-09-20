"""
Persistent memory for InboxHero.

Stores user preferences and other durable state in memory_store.json.
The memory survives process exit and restart.
"""

import json
from datetime import datetime
from pathlib import Path


MEMORY_FILE = Path(__file__).resolve().parent / "memory_store.json"


def _load_memory():
    """
    Load persistent memory from disk.
    Returns an empty dictionary if the file does not exist.
    """
    if not MEMORY_FILE.exists():
        return {}

    try:
        with MEMORY_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_memory(memory):
    """
    Save persistent memory to disk.
    """
    with MEMORY_FILE.open("w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2)


def remember(key, value, source="manual"):
    """
    Store or update a memory item.
    """
    memory = _load_memory()

    memory[key] = {
        "value": value,
        "source": source,
        "timestamp": datetime.now().isoformat(),
    }

    _save_memory(memory)

    return f"Remembered {key} = {value}"


def recall(query):
    """
    Retrieve a previously stored memory item by key.
    """
    memory = _load_memory()
    return memory.get(query)


def summarize_memory():
    """
    Return a simple human-readable summary of stored memories.
    """
    memory = _load_memory()

    return [
        f"{key}: {details.get('value')}"
        for key, details in memory.items()
    ]