"""
LiteLLM client wrapper for LLM CTF challenges.
Uses openai-python against a LiteLLM-compatible base URL.
"""

import os
from openai import OpenAI


def get_client(api_key: str) -> OpenAI:
    """Create an OpenAI-compatible client pointed at LiteLLM."""
    base_url = os.environ.get("LITELLM_BASE_URL", "http://litellm:4000/v1")
    return OpenAI(base_url=base_url, api_key=api_key)


def get_model() -> str:
    """Get the routed model name from env, defaulting to gemini-2.5-flash."""
    return os.environ.get("LITELLM_MODEL", "gemini-2.5-flash")


def chat_with_gemini(
    system_prompt: str,
    conversation_history: list[dict],
    user_message: str,
    api_key: str,
) -> str:
    """
    Send a chat completion through LiteLLM with the player's API key.

    Args:
        system_prompt: The system instruction for the model.
        conversation_history: List of {"role": "user"|"model", "text": str} dicts.
        user_message: The new user message.
        api_key: Player-supplied API key from X-Player-API-Key header.

    Returns:
        The model's response text.
    """
    client = get_client(api_key=api_key)
    model = get_model()

    messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]

    for msg in conversation_history:
        role = "assistant" if msg["role"] == "model" else "user"
        messages.append({"role": role, "content": msg["text"]})

    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7,
        max_tokens=2048,
    )

    return response.choices[0].message.content or ""
