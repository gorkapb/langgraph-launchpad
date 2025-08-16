import requests
import time
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint."""
    print("🔍 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        print("✅ Health check passed")
        return True
    else:
        print(f"❌ Health check failed: {response.status_code}")
        return False

def test_create_thread():
    """Test thread creation."""
    print("🔍 Testing thread creation...")
    response = requests.post(
        f"{BASE_URL}/api/v1/threads",
        json={"user_id": "test_user_123"}
    )
    if response.status_code == 201:
        data = response.json()
        thread_id = data["thread_id"]
        print(f"✅ Thread created successfully: {thread_id}")
        return thread_id
    else:
        print(f"❌ Thread creation failed: {response.status_code}")
        print(response.text)
        return None

def test_chat(thread_id):
    """Test chat functionality."""
    print("🔍 Testing chat...")
    response = requests.post(
        f"{BASE_URL}/api/v1/threads/{thread_id}/chat",
        json={
            "message": "Hello! Can you help me?",
            "reasoning": False
        }
    )
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Chat response: {data['response'][:100]}...")
        return True
    else:
        print(f"❌ Chat failed: {response.status_code}")
        print(response.text)
        return False

def test_get_history(thread_id):
    """Test getting thread history."""
    print("🔍 Testing thread history...")
    response = requests.get(f"{BASE_URL}/api/v1/threads/{thread_id}")
    if response.status_code == 200:
        data = response.json()
        message_count = len(data["messages"])
        print(f"✅ Thread history retrieved: {message_count} messages")
        return True
    else:
        print(f"❌ Thread history failed: {response.status_code}")
        print(response.text)
        return False

def test_list_threads():
    """Test listing all threads."""
    print("🔍 Testing thread listing...")
    response = requests.get(f"{BASE_URL}/api/v1/threads")
    if response.status_code == 200:
        data = response.json()
        thread_count = len(data["threads"])
        print(f"✅ Thread listing: {thread_count} threads found")
        return True
    else:
        print(f"❌ Thread listing failed: {response.status_code}")
        print(response.text)
        return False

def main():
    """Run all tests."""
    print("🧪 Starting API tests...\n")
    
    # Test health
    if not test_health():
        print("❌ Server is not running. Start it with 'make run'")
        return
    
    print()
    
    # Test thread creation
    thread_id = test_create_thread()
    if not thread_id:
        return
    
    print()
    
    # Test chat
    if not test_chat(thread_id):
        return
    
    print()
    
    # Test history
    if not test_get_history(thread_id):
        return
    
    print()
    
    # Test listing
    if not test_list_threads():
        return
    
    print()
    print("🎉 All tests passed!")
    print(f"📊 Thread ID for further testing: {thread_id}")

if __name__ == "__main__":
    main()