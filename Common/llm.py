"""
LLM client wrapper for InboxHero.

Supports:
- Ollama (local development)
- Google Gemini

The provider and model are configured through config.py.
"""

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

# Add project root to path so imports work
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config


# Keep a single client instance for providers that require one.
_client = None


def get_client():
    """
    Return the provider client.

    Ollama uses its HTTP API directly, so no Python client object is required.
    Gemini uses the Google GenAI client.
    """
    global _client

    if config.LLM_PROVIDER == "google":
        if _client is None:
            from google import genai

            config.require_api_key()
            _client = genai.Client(api_key=config.GOOGLE_API_KEY)

        return _client

    if config.LLM_PROVIDER == "ollama":
        # Ollama is accessed through its local HTTP API.
        return None

    raise RuntimeError(
        f"Unsupported LLM_PROVIDER: {config.LLM_PROVIDER}. "
        "Use 'ollama' or 'google'."
    )


def chat(prompt: str, system: str = None, temperature: float = None) -> str:
    """
    Send a single user prompt with an optional system instruction.

    Returns the model's text response.
    """
    if temperature is None:
        temperature = config.MODEL_TEMPERATURE

    messages = []

    if system:
        messages.append(
            {
                "role": "system",
                "content": system,
            }
        )

    messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    return chat_messages(messages, temperature=temperature)


def chat_messages(messages: list, temperature: float = None) -> str:
    """
    Send a list of messages to the configured LLM provider.

    Expected message format:

    [
        {"role": "system", "content": "..."},
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": "..."}
    ]

    Returns the model's text response.
    """
    if temperature is None:
        temperature = config.MODEL_TEMPERATURE

    if config.LLM_PROVIDER == "ollama":
        return _chat_ollama(messages, temperature)

    if config.LLM_PROVIDER == "google":
        return _chat_google(messages, temperature)

    raise RuntimeError(
        f"Unsupported LLM_PROVIDER: {config.LLM_PROVIDER}. "
        "Use 'ollama' or 'google'."
    )


def _chat_ollama(messages: list, temperature: float) -> str:
    """
    Send messages to the locally running Ollama server.
    """
    payload = {
        "model": config.MODEL_NAME,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": temperature,
        },
    }

    request = urllib.request.Request(
        url=f"{config.OLLAMA_BASE_URL.rstrip('/')}/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            response_data = json.loads(
                response.read().decode("utf-8")
            )

    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")

        raise RuntimeError(
            f"Ollama HTTP error {exc.code}: {error_body}"
        ) from exc

    except urllib.error.URLError as exc:
        raise RuntimeError(
            "Could not connect to Ollama at "
            f"{config.OLLAMA_BASE_URL}. "
            "Make sure Ollama is running and the configured model "
            f"'{config.MODEL_NAME}' is available."
        ) from exc

    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "Ollama returned an invalid JSON response."
        ) from exc

    message = response_data.get("message", {})
    content = message.get("content", "")

    if not content:
        raise RuntimeError(
            f"Ollama returned no model content: {response_data}"
        )

    return content.strip()


def _chat_google(messages: list, temperature: float) -> str:
    """
    Send messages to Google Gemini using the Google GenAI SDK.
    """
    from google.genai import types

    system_parts = []
    contents = []

    for message in messages:
        role = message["role"]
        text = message["content"]

        if role == "system":
            system_parts.append(text)

        elif role == "assistant":
            contents.append(
                types.Content(
                    role="model",
                    parts=[types.Part(text=text)],
                )
            )

        else:
            contents.append(
                types.Content(
                    role="user",
                    parts=[types.Part(text=text)],
                )
            )

    generate_config = {
        "temperature": temperature,
        "automatic_function_calling": (
            types.AutomaticFunctionCallingConfig(
                disable=True
            )
        ),
    }

    if system_parts:
        generate_config["system_instruction"] = "\n\n".join(
            system_parts
        )

    response = get_client().models.generate_content(
        model=config.MODEL_NAME,
        contents=contents,
        config=types.GenerateContentConfig(
            **generate_config
        ),
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")

    return response.text.strip()