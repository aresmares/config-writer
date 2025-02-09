from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import Engine, create_engine

# DATABASE_URL = "sqlite:///./config.db"


class Settings(BaseSettings):
    # Application settings
    host: str = "localhost"
    port: int = 8000

    # Logging settings
    log_level: str = "INFO"

    database_url: str = "sqlite:///./config.db"

    engine: Engine = create_engine(
        database_url, connect_args={"check_same_thread": False}, echo=True
    )

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings():
    return Settings()
