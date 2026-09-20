"""
Gemini client wrapper for SkyVault Agent.
Handles connection setup and sending prompts/messages to the model.
"""

import sys
from pathlib import Path

# Add project root to path so imports work
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from google import genai
from google.genai import types

import config

# Keep a single client instance
_client = None


def get_client():
    """
    Return a Gemini client. Create it once using the API key from config.py.
    """
    global _client
    if _client is None:
        config.require_api_key()
        _client = genai.Client(api_key=config.GOOGLE_API_KEY)
    return _client


def chat(prompt: str, system: str = None, temperature: float = None) -> str:
    """
    Send a single user prompt (with optional system persona) to Gemini.
    Returns the model's text reply.
    """
    if temperature is None:
        temperature = config.MODEL_TEMPERATURE

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    return chat_messages(messages, temperature=temperature)


def chat_messages(messages: list, temperature: float = None) -> str:
    """
    Send a list of messages (system, user, assistant) to Gemini.
    Returns the model's text reply.
    """
    if temperature is None:
        temperature = config.MODEL_TEMPERATURE

    system_parts = []
    contents = []

    # Convert messages into Gemini Content objects
    for message in messages:
        role = message["role"]
        text = message["content"]

        if role == "system":
            system_parts.append(text)
        elif role == "assistant":
            contents.append(types.Content(role="model", parts=[types.Part(text=text)]))
        else:  # user
            contents.append(types.Content(role="user", parts=[types.Part(text=text)]))

    # Build generation config
    generate_config = {
        "temperature": temperature,
        "automatic_function_calling": types.AutomaticFunctionCallingConfig(disable=True),
    }
    if system_parts:
        generate_config["system_instruction"] = "\n\n".join(system_parts)

    # Call Gemini
    response = get_client().models.generate_content(
        model=config.MODEL_NAME,
        contents=contents,
        config=types.GenerateContentConfig(**generate_config),
    )

    return response.text
