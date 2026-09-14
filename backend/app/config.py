from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    sarvam_api_key: str
    sarvam_base_url: str = "https://api.sarvam.ai/v1"
    sarvam_chat_model: str = "sarvam-105b"

    database_url: str = "sqlite:///./kivi.db"
    
    # Allow cors_origin to accept either a list or a comma-separated string
    cors_origins: Union[str, List[str]] = "http://localhost:5173,https://kivi-theta.vercel.app"
    jwt_secret_key: str = "dev-only-insecure-secret-change-in-prod"

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"  # Prevents crashes if extra env vars exist
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            # Split comma-separated string and remove trailing slashes
            return [origin.strip().rstrip("/") for origin in v.split(",") if origin.strip()]
        return [origin.rstrip("/") for origin in v]


settings = Settings()