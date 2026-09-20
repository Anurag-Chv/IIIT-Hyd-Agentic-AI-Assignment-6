"""
Configuration loader for InboxHero.
Reads environment variables from .env and makes them available in Python.
"""

import os
from pathlib import Path


def load_env_file():
    """
    Read the .env file line by line and set variables into os.environ.
    Skips comments and blank lines.
    """
    env_path = Path(__file__).resolve().parent / ".env"

    if not env_path.exists():
        return

    with env_path.open("r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()

            # Ignore empty lines, comments, and invalid lines
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip("'").strip('"')

            # Do not overwrite variables already present in the environment
            if key and key not in os.environ:
                os.environ[key] = value


# Load variables at import time
load_env_file()


# ------------------------------------------------------------------
# LLM configuration
# ------------------------------------------------------------------

# Supported providers can include:
#   ollama
#   google
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "ollama").lower()

# Default local model for Assignment 6 development
MODEL_NAME = os.environ.get("MODEL_NAME", "qwen2.5:7b")

# Ollama configuration
OLLAMA_BASE_URL = os.environ.get(
    "OLLAMA_BASE_URL",
    "http://localhost:11434"
)

# Google Gemini configuration (kept available if needed)
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")

# Model generation settings
MODEL_TEMPERATURE = float(
    os.environ.get("MODEL_TEMPERATURE", "0.2")
)

# Maximum number of agent/tool interaction rounds
MAX_TOOL_ROUNDS = int(
    os.environ.get("MAX_TOOL_ROUNDS", "8")
)


def require_api_key():
    """
    Raise an error only when Google is selected as the LLM provider.
    Ollama does not require an API key.
    """
    if LLM_PROVIDER != "google":
        return

    if not GOOGLE_API_KEY:
        raise RuntimeError(
            "Missing GOOGLE_API_KEY. Please set it in .env "
            "(copy from .env.example)."
        )