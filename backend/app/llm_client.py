from openai import OpenAI

from app.config import settings

client = OpenAI(
    api_key=settings.sarvam_api_key,
    base_url=settings.sarvam_base_url,
)


def chat(messages: list[dict], temperature: float = 0.2, reasoning_effort=None) -> dict:
    """Thin wrapper around Sarvam's OpenAI-compatible chat completions endpoint."""
    response = client.chat.completions.create(
        model=settings.sarvam_chat_model,
        messages=messages,
        temperature=temperature,
        reasoning_effort=reasoning_effort,  # None disables thinking mode (faster/cheaper)
    )
    choice = response.choices[0].message
    usage = response.usage
    return {
        "content": choice.content,
        "prompt_tokens": usage.prompt_tokens if usage else None,
        "completion_tokens": usage.completion_tokens if usage else None,
    }