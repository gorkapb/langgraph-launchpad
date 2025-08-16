import os
import pytest

from src.langgraph_launchpad.config.settings import Settings, get_settings


def test_settings_defaults():
    """Test default settings values."""
    settings = Settings()
    
    assert settings.database_type == "sqlite"
    assert settings.host == "0.0.0.0"
    assert settings.port == 8000
    assert settings.debug is False
    assert settings.log_level == "INFO"


def test_settings_from_env():
    """Test settings loaded from environment variables."""
    # Set environment variables
    os.environ["DATABASE_TYPE"] = "postgresql"
    os.environ["HOST"] = "127.0.0.1"
    os.environ["PORT"] = "9000"
    os.environ["DEBUG"] = "true"
    
    try:
        settings = Settings()
        
        assert settings.database_type == "postgresql"
        assert settings.host == "127.0.0.1"
        assert settings.port == 9000
        assert settings.debug is True
    finally:
        # Cleanup
        for key in ["DATABASE_TYPE", "HOST", "PORT", "DEBUG"]:
            os.environ.pop(key, None)


def test_settings_database_type_properties():
    """Test database type property methods."""
    sqlite_settings = Settings(database_type="sqlite")
    postgresql_settings = Settings(database_type="postgresql")
    
    assert sqlite_settings.is_sqlite is True
    assert sqlite_settings.is_postgresql is False
    
    assert postgresql_settings.is_sqlite is False
    assert postgresql_settings.is_postgresql is True


def test_get_settings_cached():
    """Test that get_settings returns cached instance."""
    settings1 = get_settings()
    settings2 = get_settings()
    
    assert settings1 is settings2