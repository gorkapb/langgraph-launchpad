import os
import tempfile
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.langgraph_launchpad.core.database import Base, get_db
from src.langgraph_launchpad.main import create_app


@pytest.fixture
def temp_db() -> Generator[str, None, None]:
    """Create a temporary SQLite database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        temp_db_path = tmp.name
    
    # Override DATABASE_URL for testing
    os.environ["DATABASE_URL"] = f"sqlite:///{temp_db_path}"
    
    yield temp_db_path
    
    # Cleanup
    try:
        os.unlink(temp_db_path)
    except OSError:
        pass


@pytest.fixture
def test_engine(temp_db):
    """Create test database engine."""
    engine = create_engine(
        f"sqlite:///{temp_db}",
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture
def test_session(test_engine) -> Generator[Session, None, None]:
    """Create test database session."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, 
        autoflush=False, 
        bind=test_engine
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(test_session) -> Generator[TestClient, None, None]:
    """Create test client with overridden dependencies."""
    app = create_app()
    
    # Override database dependency
    def override_get_db():
        try:
            yield test_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_thread_data():
    """Sample thread data for testing."""
    return {"user_id": "test_user_123"}


@pytest.fixture
def sample_chat_data():
    """Sample chat data for testing."""
    return {
        "message": "Hello, this is a test message!",
        "reasoning": False
    }