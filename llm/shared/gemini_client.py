"""
Gemini API client wrapper for LLM CTF challenges.
Uses the google-genai unified SDK.
"""

import os
from google import genai
from google.genai import types


def get_client() -> genai.Client:
    """Create a Gemini client using the GEMINI_API_KEY env var."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable is not set")
    return genai.Client(api_key=api_key)


def get_model() -> str:
    """Get the model name from env, defaulting to gemini-2.5-flash."""
    return os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")


def chat_with_gemini(
    system_prompt: str,
    conversation_history: list[dict],
    user_message: str,
) -> str:
    """
    Send a message to Gemini with a system prompt and conversation history.

    Args:
        system_prompt: The system instruction for the model.
        conversation_history: List of {"role": "user"|"model", "text": str} dicts.
        user_message: The new user message.

    Returns:
        The model's response text.
    """
    client = get_client()
    model = get_model()

    contents = []
    for msg in conversation_history:
        contents.append(
            types.Content(
                role=msg["role"],
                parts=[types.Part.from_text(text=msg["text"])],
            )
        )

    contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_message)],
        )
    )

    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.7,
            max_output_tokens=65536,
        ),
    )

    return response.text or ""
