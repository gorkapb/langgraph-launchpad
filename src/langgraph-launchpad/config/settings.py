import os
from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Database configuration
    database_type: Literal["sqlite", "postgresql"] = Field(
        default="sqlite",
        description="Database type to use"
    )
    database_url: str = Field(
        default="sqlite:///./threads.db",
        description="Database connection URL"
    )
    
    # API configuration
    host: str = Field(default="0.0.0.0", description="API host")
    port: int = Field(default=8000, description="API port")
    debug: bool = Field(default=False, description="Debug mode")
    
    # Logging configuration
    log_level: str = Field(default="INFO", description="Logging level")
    
    # LangGraph configuration
    openai_api_key: str = Field(default="", description="OpenAI API key")
    
    @property
    def is_sqlite(self) -> bool:
        """Check if using SQLite database."""
        return self.database_type == "sqlite"
    
    @property
    def is_postgresql(self) -> bool:
        """Check if using PostgreSQL database."""
        return self.database_type == "postgresql"


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()