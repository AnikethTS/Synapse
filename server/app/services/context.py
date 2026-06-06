"""
Context window management: token estimation, history trimming, and
conversation summarization.
"""

import logging

from groq import Groq

from app.core.config import get_settings
from app.core.prompts import SUMMARIZE_PROMPT
from app.models.chat import Message

logger = logging.getLogger(__name__)

GroqMessage = dict[str, str]



def estimate_tokens(text: str) -> int:
    """
    O(n) approximation: 1 token ≈ 4 UTF-8 characters for English prose.
    Accurate enough for budget decisions without a full tokenizer dependency.
    """
    return max(1, len(text) // 4)


def preprocess(messages: list[Message]) -> list[GroqMessage]:
    """
    Strip whitespace, enforce the per-message character cap, and drop empty
    turns. Returns plain dicts ready for the Groq API.

    Raises ValueError if every message is empty after sanitization.
    """
    cfg = get_settings()
    result: list[GroqMessage] = []

    for m in messages:
        content = m.content.strip()
        if not content:
            continue
        if len(content) > cfg.max_message_chars:
            content = content[: cfg.max_message_chars] + "\n[Message truncated — input too long]"
        result.append({"role": m.role, "content": content})

    if not result:
        raise ValueError("All messages were empty after sanitization")

    return result


def trim_to_budget(messages: list[GroqMessage]) -> list[GroqMessage]:
    """
    Greedy reverse scan: walk messages newest → oldest, accumulating token cost
    until MAX_CONTEXT_TOKENS is exhausted. The result is the largest suffix of
    the conversation that fits within the budget.

    If messages were dropped, two framing turns are prepended so the model
    knows the conversation was truncated and doesn't hallucinate earlier context.
    """
    cfg = get_settings()
    budget = cfg.max_context_tokens
    kept: list[GroqMessage] = []

    for msg in reversed(messages):
        cost = estimate_tokens(msg["content"])
        if kept and budget - cost < 0:
            break
        budget -= cost
        kept.append(msg)

    kept.reverse()

    if len(kept) < len(messages):
        logger.info(
            "Context trimmed: %d → %d messages (%d tokens remaining in budget)",
            len(messages),
            len(kept),
            budget,
        )
        kept = [
            {"role": "user", "content": "[Earlier messages omitted — context window full]"},
            {"role": "assistant", "content": "Understood. I'll work from the available context."},
            *kept,
        ]

    return kept


def _summarize(client: Groq, messages: list[GroqMessage]) -> str:
    """Non-streaming Groq call that returns a compact summary of older turns."""
    transcript = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in messages)
    response = client.chat.completions.create(
        model=get_settings().groq_model,
        messages=[
            {"role": "system", "content": SUMMARIZE_PROMPT},
            {"role": "user", "content": transcript},
        ],
        stream=False,
        temperature=0.3,
        max_tokens=512,
    )
    return response.choices[0].message.content or ""


def maybe_summarize(client: Groq, messages: list[GroqMessage]) -> list[GroqMessage]:
    """
    When history exceeds SUMMARY_THRESHOLD messages, split at the midpoint,
    summarize the older half, and replace it with a single assistant turn.

    This preserves the substance of earlier turns better than blind truncation
    while keeping the payload sent to the model bounded.
    """
    cfg = get_settings()
    if len(messages) <= cfg.summary_threshold:
        return messages

    split = len(messages) // 2
    old, recent = messages[:split], messages[split:]

    logger.info("Summarizing %d older messages (of %d total)", split, len(messages))
    summary = _summarize(client, old)

    return [
        {"role": "assistant", "content": f"[Summary of earlier conversation]\n{summary}"},
        *recent,
    ]
