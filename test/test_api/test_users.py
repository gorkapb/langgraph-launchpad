import pytest
from fastapi.testclient import TestClient


def test_get_all_users_empty(client: TestClient):
    """Test getting all users when none exist."""
    response = client.get("/api/v1/users")
    
    assert response.status_code == 200
    data = response.json()
    assert data["users"] == []
    assert data["total"] == 0


def test_get_all_users(client: TestClient):
    """Test getting all users."""
    # Create threads for different users
    users = ["user1", "user2", "user3"]
    for user in users:
        client.post("/api/v1/threads", json={"user_id": user})
    
    response = client.get("/api/v1/users")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["users"]) == len(users)
    assert all(user in data["users"] for user in users)


def test_get_user_threads(client: TestClient):
    """Test getting threads for a specific user."""
    user_id = "test_user"
    
    # Create threads for the user
    for i in range(2):
        client.post("/api/v1/threads", json={"user_id": user_id})
    
    response = client.get(f"/api/v1/users/{user_id}/threads")
    
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == user_id
    assert len(data["threads"]) == 2
    assert data["total"] == 2


def test_get_nonexistent_user_threads(client: TestClient):
    """Test getting threads for a nonexistent user."""
    response = client.get("/api/v1/users/nonexistent_user/threads")
    
    assert response.status_code == 404