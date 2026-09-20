# memory.py
# Roll number: evernorth-aai-1155338

import json
import os
from datetime import datetime

MEMORY_FILE = "memory_store.json"

def _load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def _save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

def remember(key, value, source="manual"):
    memory = _load_memory()
    memory[key] = {
        "value": value,
        "source": source,
        "timestamp": datetime.now().isoformat()
    }
    _save_memory(memory)
    return f"Remembered {key} = {value}"

def recall(query):
    memory = _load_memory()
    return memory.get(query, None)

def summarize_memory():
    memory = _load_memory()
    return [f"{k}: {v['value']}" for k, v in memory.items()]
