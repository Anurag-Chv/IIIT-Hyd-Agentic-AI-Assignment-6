import json
import urllib.error
import urllib.request

import config


_client = None


def get_client():
    global _client

    if config.LLM_PROVIDER == "google":
        if _client is None:
            from google import genai

            config.require_api_key()
            _client = genai.Client(api_key=config.GOOGLE_API_KEY)

        return _client

    if config.LLM_PROVIDER == "ollama":
        return None

    raise RuntimeError(
        f"Unsupported LLM_PROVIDER: {config.LLM_PROVIDER}"
    )


def chat(prompt, system=None, temperature=None):
    messages = []

    if system:
        messages.append({
            "role": "system",
            "content": system,
        })

    messages.append({
        "role": "user",
        "content": prompt,
    })

    return chat_messages(messages, temperature)


def chat_messages(messages, temperature=None):
    temperature = (
        config.MODEL_TEMPERATURE
        if temperature is None
        else temperature
    )

    if config.LLM_PROVIDER == "ollama":
        return _chat_ollama(messages, temperature)

    if config.LLM_PROVIDER == "google":
        return _chat_google(messages, temperature)

    raise RuntimeError(
        f"Unsupported LLM_PROVIDER: {config.LLM_PROVIDER}"
    )


def _chat_ollama(messages, temperature):
    payload = {
        "model": config.MODEL_NAME,
        "messages": messages,
        "stream": False,
        "options": {"temperature": temperature},
    }

    request = urllib.request.Request(
        f"{config.OLLAMA_BASE_URL.rstrip('/')}/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            data = json.loads(response.read().decode("utf-8"))

    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"Ollama HTTP error {exc.code}: {body}"
        ) from exc

    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"Could not connect to Ollama at {config.OLLAMA_BASE_URL}. "
            f"Make sure '{config.MODEL_NAME}' is available."
        ) from exc

    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "Ollama returned invalid JSON."
        ) from exc

    content = data.get("message", {}).get("content", "")

    if not content:
        raise RuntimeError("Ollama returned no model content.")

    return content.strip()


def _chat_google(messages, temperature):
    from google.genai import types

    system_parts = []
    contents = []

    for message in messages:
        role = message["role"]
        text = message["content"]

        if role == "system":
            system_parts.append(text)
        else:
            contents.append(
                types.Content(
                    role="model" if role == "assistant" else "user",
                    parts=[types.Part(text=text)],
                )
            )

    config_data = {
        "temperature": temperature,
        "automatic_function_calling": (
            types.AutomaticFunctionCallingConfig(disable=True)
        ),
    }

    if system_parts:
        config_data["system_instruction"] = "\n\n".join(system_parts)

    response = get_client().models.generate_content(
        model=config.MODEL_NAME,
        contents=contents,
        config=types.GenerateContentConfig(**config_data),
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")

    return response.text.strip()