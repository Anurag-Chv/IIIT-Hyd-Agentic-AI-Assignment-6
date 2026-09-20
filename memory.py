import json
from datetime import datetime
from pathlib import Path


MEMORY_FILE = Path(__file__).resolve().parent / "memory_store.json"


def _load_memory():
    if not MEMORY_FILE.exists():
        return {}

    try:
        with MEMORY_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_memory(data):
    with MEMORY_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def remember(key, value, source="manual"):
    data = _load_memory()

    data[key] = {
        "value": value,
        "source": source,
        "timestamp": datetime.now().isoformat(),
    }

    _save_memory(data)

    return f"Remembered {key} = {value}"


def recall(query):
    return _load_memory().get(query)


def summarize_memory():
    return [
        f"{key}: {details.get('value')}"
        for key, details in _load_memory().items()
    ]