from groq import Groq

from app.core.config import get_settings

_client: Groq | None = None


def get_groq_client() -> Groq:
    """Lazy singleton — instantiated once on first request."""
    global _client
    if _client is None:
        _client = Groq(api_key=get_settings().groq_api_key)
    return _client
