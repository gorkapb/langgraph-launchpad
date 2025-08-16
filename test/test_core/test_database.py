import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.langgraph_launchpad.core.database import create_tables
from src.langgraph_launchpad.core.models import Thread


def test_create_tables(test_engine):
    """Test table creation."""
    create_tables()
    
    # Check if tables exist
    with test_engine.connect() as conn:
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result]
    
    assert "threads" in tables


def test_thread_model(test_session: Session):
    """Test Thread model basic functionality."""
    # Create a thread
    thread = Thread(user_id="test_user")
    test_session.add(thread)
    test_session.commit()
    test_session.refresh(thread)
    
    assert thread.thread_id is not None
    assert thread.user_id == "test_user"
    assert thread.created_at is not None
    assert thread.updated_at is not None


def test_thread_model_repr(test_session: Session):
    """Test Thread model string representation."""
    thread = Thread(user_id="test_user")
    test_session.add(thread)
    test_session.commit()
    test_session.refresh(thread)
    
    repr_str = repr(thread)
    assert "Thread" in repr_str
    assert str(thread.thread_id) in repr_str
    assert "test_user" in repr_str