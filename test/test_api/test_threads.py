import pytest
from fastapi.testclient import TestClient

from src.langgraph_launchpad.core.models import Thread


def test_create_thread(client: TestClient, sample_thread_data):
    """Test thread creation."""
    response = client.post("/api/v1/threads", json=sample_thread_data)
    
    assert response.status_code == 201
    data = response.json()
    assert "thread_id" in data
    assert data["user_id"] == sample_thread_data["user_id"]
    assert "created_at" in data


def test_create_thread_invalid_data(client: TestClient):
    """Test thread creation with invalid data."""
    response = client.post("/api/v1/threads", json={})
    
    assert response.status_code == 422  # Validation error


def test_get_thread_history(client: TestClient, test_session, sample_thread_data):
    """Test getting thread history."""
    # First create a thread
    response = client.post("/api/v1/threads", json=sample_thread_data)
    thread_id = response.json()["thread_id"]
    
    # Get thread history
    response = client.get(f"/api/v1/threads/{thread_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["thread_id"] == thread_id
    assert data["user_id"] == sample_thread_data["user_id"]
    assert isinstance(data["messages"], list)


def test_get_nonexistent_thread(client: TestClient):
    """Test getting a nonexistent thread."""
    response = client.get("/api/v1/threads/99999")
    
    assert response.status_code == 404


def test_get_all_threads(client: TestClient, sample_thread_data):
    """Test getting all threads."""
    # Create a few threads
    for i in range(3):
        client.post("/api/v1/threads", json={"user_id": f"user_{i}"})
    
    response = client.get("/api/v1/threads")
    
    assert response.status_code == 200
    data = response.json()
    assert "threads" in data
    assert "total" in data
    assert len(data["threads"]) >= 3


def test_delete_thread(client: TestClient, sample_thread_data):
    """Test thread deletion."""
    # Create a thread
    response = client.post("/api/v1/threads", json=sample_thread_data)
    thread_id = response.json()["thread_id"]
    
    # Delete the thread
    response = client.delete(f"/api/v1/threads/{thread_id}")
    
    assert response.status_code == 204
    
    # Verify it's deleted
    response = client.get(f"/api/v1/threads/{thread_id}")
    assert response.status_code == 404


def test_delete_nonexistent_thread(client: TestClient):
    """Test deleting a nonexistent thread."""
    response = client.delete("/api/v1/threads/99999")
    
    assert response.status_code == 404