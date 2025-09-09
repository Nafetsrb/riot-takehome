from __future__ import annotations
import logging
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application configuration loaded from environment (.env supported)."""

    hmac_secret: str = Field('', alias='RIOT_HMAC_SECRET')
    log_level_str: str = Field('INFO', alias='APP_LOG_LEVEL')
    max_body_bytes: int = Field(2 * 1024 * 1024, alias='APP_MAX_BODY_BYTES')

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
    )

    @property
    def log_level(self) -> int:
        return getattr(logging, self.log_level_str.upper(), logging.INFO)

settings = Settings()
