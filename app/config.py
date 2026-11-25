"""Application configuration loaded from environment / .env file."""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Reddit
    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    reddit_user_agent: str = "social-listening-tool/0.1"

    # YouTube
    youtube_api_key: str = ""

    # News API
    newsapi_key: str = ""

    # Mastodon
    mastodon_instance: str = "https://mastodon.social"
    mastodon_access_token: str = ""

    # Bluesky
    bluesky_identifier: str = ""
    bluesky_app_password: str = ""

    # App
    database_path: str = "social_listening.db"


settings = Settings()
