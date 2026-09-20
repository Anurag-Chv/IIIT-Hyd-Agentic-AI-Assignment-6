"""
Configuration loader for SkyVault Agent.
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

    with env_path.open("r") as f:
        for raw_line in f:
            line = raw_line.strip()
            # Ignore empty lines or comments
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip("'").strip('"')

            # Only set if not already in environment
            if key and key not in os.environ:
                os.environ[key] = value


# Load variables at import time
load_env_file()

# Expose configuration values
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
MODEL_NAME = os.environ.get("MODEL_NAME", "gemini-3.6-flash")
MODEL_TEMPERATURE = float(os.environ.get("MODEL_TEMPERATURE", "0.2"))
MAX_TOOL_ROUNDS = int(os.environ.get("MAX_TOOL_ROUNDS", "8"))


def require_api_key():
    """
    Raise an error if the API key is missing.
    Ensures you don’t accidentally run without credentials.
    """
    if not GOOGLE_API_KEY:
        raise RuntimeError(
            "Missing GOOGLE_API_KEY. Please set it in .env (copy from .env.example)."
        )
