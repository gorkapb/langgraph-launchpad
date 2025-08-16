import pytest
from fastapi.testclient import TestClient


def test_chat_basic(client: TestClient, sample_chat_data):
    """Test basic chat functionality."""
    # Create a thread first
    thread_response = client.post("/api/v1/threads", json={"user_id": "test_user"})
    thread_id = thread_response.json()["thread_id"]
    
    # Send a chat message
    response = client.post(f"/api/v1/threads/{thread_id}/chat", json=sample_chat_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert data["thread_id"] == thread_id
    assert isinstance(data["response"], str)
    assert len(data["response"]) > 0


def test_chat_with_reasoning(client: TestClient):
    """Test chat with reasoning enabled."""
    # Create a thread first
    thread_response = client.post("/api/v1/threads", json={"user_id": "test_user"})
    thread_id = thread_response.json()["thread_id"]
    
    chat_data = {
        "message": "Explain quantum computing",
        "reasoning": True
    }
    
    response = client.post(f"/api/v1/threads/{thread_id}/chat", json=chat_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert data["thread_id"] == thread_id


def test_chat_nonexistent_thread(client: TestClient, sample_chat_data):
    """Test chat with nonexistent thread."""
    response = client.post("/api/v1/threads/99999/chat", json=sample_chat_data)
    
    assert response.status_code == 404


def test_chat_invalid_data(client: TestClient):
    """Test chat with invalid data."""
    # Create a thread first
    thread_response = client.post("/api/v1/threads", json={"user_id": "test_user"})
    thread_id = thread_response.json()["thread_id"]
    
    # Send invalid chat data
    response = client.post(f"/api/v1/threads/{thread_id}/chat", json={})
    
    assert response.status_code == 422  # Validation error


def test_chat_streaming_setup(client: TestClient, sample_chat_data):
    """Test streaming chat endpoint setup."""
    # Create a thread first
    thread_response = client.post("/api/v1/threads", json={"user_id": "test_user"})
    thread_id = thread_response.json()["thread_id"]
    
    # Test streaming endpoint (this will test the endpoint exists and handles the request)
    response = client.post(f"/api/v1/threads/{thread_id}/chat/stream", json=sample_chat_data)
    
    # The response should be a streaming response
    assert response.status_code == 200