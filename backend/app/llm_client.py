from openai import OpenAI

from app.config import settings

client = OpenAI(
    api_key=settings.sarvam_api_key,
    base_url=settings.sarvam_base_url,
)


def chat(messages: list[dict], temperature: float = 0.2, reasoning: bool = False) -> dict:
    """Thin wrapper around Sarvam's OpenAI-compatible chat completions endpoint.

    reasoning=False (default) disables Sarvam's thinking mode via extra_body,
    since most of our calls (extraction, tool routing, polishing) are latency/
    cost-sensitive and don't need deep reasoning.
    """
    extra_body = {} if reasoning else {"reasoning_effort": None}

    response = client.chat.completions.create(
        model=settings.sarvam_chat_model,
        messages=messages,
        temperature=temperature,
        extra_body=extra_body,
    )
    choice = response.choices[0].message
    usage = response.usage
    return {
        "content": choice.content,
        "prompt_tokens": usage.prompt_tokens if usage else None,
        "completion_tokens": usage.completion_tokens if usage else None,
    }