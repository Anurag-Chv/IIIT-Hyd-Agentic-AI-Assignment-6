import os
from pathlib import Path


def load_env_file():
    env_file = Path(__file__).resolve().parent / ".env"

    if not env_file.exists():
        return

    with env_file.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("#") or "=" not in line:
                continue

            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip("'\"")

            if key and key not in os.environ:
                os.environ[key] = value


load_env_file()

LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "ollama").lower()
MODEL_NAME = os.environ.get("MODEL_NAME", "qwen2.5:7b")
OLLAMA_BASE_URL = os.environ.get(
    "OLLAMA_BASE_URL",
    "http://localhost:11434",
)
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
MODEL_TEMPERATURE = float(os.environ.get("MODEL_TEMPERATURE", "0.2"))
MAX_TOOL_ROUNDS = int(os.environ.get("MAX_TOOL_ROUNDS", "8"))


def require_api_key():
    if LLM_PROVIDER == "google" and not GOOGLE_API_KEY:
        raise RuntimeError(
            "Missing GOOGLE_API_KEY. Set it in .env."
        )