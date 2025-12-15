from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    env: str = Field(default="dev", validation_alias="ENV")
    frontend_origin: str | None = Field(default=None, validation_alias="FRONTEND_ORIGIN")
    telegram_bot_token: str | None = Field(default=None, validation_alias="TELEGRAM_BOT_TOKEN")
    telegram_webhook_secret: str | None = Field(default=None, validation_alias="TELEGRAM_WEBHOOK_SECRET")
    telegram_chat_ids_raw: str | None = Field(default=None, validation_alias="TELEGRAM_CHAT_ID")
    redis_url: str | None = Field(default=None, validation_alias="REDIS_URL")
    promo_code_ttl_days: int = Field(default=30, validation_alias="PROMO_CODE_TTL_DAYS")
    promo_code_length: int = Field(default=5, validation_alias="PROMO_CODE_LENGTH")
    letsencrypt_email: str | None = Field(default=None, validation_alias="LETSENCRYPT_EMAIL")
    domain: str | None = Field(default=None, validation_alias="DOMAIN")
    game_difficulty_level: int = Field(default=2, validation_alias="GAME_DIFFICULTY_LEVEL")

    model_config = SettingsConfigDict(env_file="../../.env", env_file_encoding="utf-8", extra="ignore")

    @property
    def allowed_origins(self) -> List[str]:
        if self.frontend_origin:
            return [self.frontend_origin]
        if self.env == "dev":
            return [
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "https://localhost:3000",
            ]
        return []

    @property
    def telegram_chat_ids(self) -> List[str]:
        if not self.telegram_chat_ids_raw:
            return []
        return [chat_id.strip() for chat_id in self.telegram_chat_ids_raw.split(",") if chat_id.strip()]

    @property
    def ai_mistake_probability(self) -> float:
        level = max(1, min(3, self.game_difficulty_level))
        mapping = {
            1: 0.85,  # около 80% побед игрока
            2: 0.45,
            3: 0.05,
        }
        return mapping[level]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
