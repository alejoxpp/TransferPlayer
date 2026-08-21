"""Configuración centralizada con pydantic-settings."""
from functools import lru_cache

from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings cargados desde .env y variables de entorno."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    neon_database_url: PostgresDsn
    db_name: str = "transferplayer"

    # Neon API
    neon_api_key: str | None = None

    # Football API (API-Football via RapidAPI)
    football_api_key: str | None = None
    football_api_host: str = "v3.football.api-sports.io"

    # App
    app_env: str = "development"
    streamlit_server_port: int = 8501
    streamlit_server_headless: bool = True

    # Optional: Supabase Auth
    supabase_url: str | None = None
    supabase_anon_key: str | None = None

    @field_validator("neon_database_url", mode="before")
    @classmethod
    def validate_db_url(cls, v: str) -> str:
        if not v or v == "postgresql://user:pass@ep-xxx.pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require":
            raise ValueError("NEON_DATABASE_URL debe configurarse en .env")
        return v

    @property
    def async_database_url(self) -> str:
        """URL convertida a asyncpg para SQLAlchemy async."""
        url = str(self.neon_database_url)
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"

    @property
    def football_headers(self) -> dict:
        """Headers para API-Football."""
        if not self.football_api_key:
            return {}
        return {
            "X-RapidAPI-Key": self.football_api_key,
            "X-RapidAPI-Host": self.football_api_host,
        }


@lru_cache
def get_settings() -> Settings:
    """Singleton de settings (cacheado)."""
    return Settings()


settings = get_settings()
