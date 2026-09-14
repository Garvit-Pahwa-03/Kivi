from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    sarvam_api_key: str
    sarvam_base_url: str = "https://api.sarvam.ai/v1"
    sarvam_chat_model: str = "sarvam-105b"

    database_url: str = "sqlite:///./kivi.db"
    cors_origin: str = "https://kivi-theta.vercel.app"
    jwt_secret_key: str = "dev-only-insecure-secret-change-in-prod"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()