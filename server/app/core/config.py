from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    groq_api_key: str

    # Model
    groq_model: str = "llama-3.3-70b-versatile"

    max_context_tokens: int = 6_000
    summary_threshold: int = 20
    max_message_chars: int = 8_000
    rate_limit_requests: int = 20
    rate_limit_window_s: int = 60
    max_retries: int = 3
    retry_base_delay_s: float = 0.5

    # CORS — set as JSON array in env: CORS_ORIGINS='["https://example.com"]'
    cors_origins: list[str] = ["http://localhost:5173"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
