from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    HYPERBROWSER_API_KEY: str = ""
    PROXY_SERVER_URL: Optional[str] = None
    PROXY_SERVER_USERNAME: Optional[str] = None
    PROXY_SERVER_PASSWORD: Optional[str] = None
    PROFILE_ID: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=[
            ".env",
            ".profile",
        ],
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )


settings = Settings()
