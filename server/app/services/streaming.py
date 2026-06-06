"""
SSE streaming with exponential-backoff retry.
"""

import logging
import time
from collections.abc import Generator

from groq import Groq

from app.core.config import get_settings

logger = logging.getLogger(__name__)

GroqMessage = dict[str, str]


def stream_with_retry(client: Groq, messages: list[GroqMessage]) -> Generator[str, None, None]:
    """
    Yield SSE-formatted chunks from Groq, retrying on transient failures with
    exponential backoff.

    Retries are safe here because this generator is evaluated lazily inside
    StreamingResponse — no data has reached the client when a connection to
    Groq fails, so we can start the stream from scratch on each attempt.

    Backoff schedule (base=0.5s): attempt 1 → 0.5s, attempt 2 → 1s, attempt 3 → 2s.
    On total failure a user-readable error event is emitted so the frontend can
    surface it rather than receiving a silent broken stream.
    """
    cfg = get_settings()
    last_exc: Exception | None = None

    for attempt in range(cfg.max_retries):
        try:
            with client.chat.completions.create(
                model=cfg.groq_model,
                messages=messages,
                stream=True,
                temperature=0.7,
                max_tokens=4096,
            ) as stream:
                for chunk in stream:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        escaped = delta.content.replace("\n", "\\n")
                        yield f"data: {escaped}\n\n"

            yield "data: [DONE]\n\n"
            return

        except Exception as exc:
            last_exc = exc
            if attempt < cfg.max_retries - 1:
                delay = cfg.retry_base_delay_s * (2**attempt)
                logger.warning(
                    "Groq request failed (attempt %d/%d), retrying in %.1fs — %s",
                    attempt + 1,
                    cfg.max_retries,
                    delay,
                    exc,
                )
                time.sleep(delay)

    logger.error("All %d attempts failed: %s", cfg.max_retries, last_exc)
    yield "data: [ERROR] The AI service is temporarily unavailable. Please try again.\n\n"
    yield "data: [DONE]\n\n"
