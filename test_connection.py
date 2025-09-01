#!/usr/bin/env python3
"""
Quick connection test script to verify backend is working
"""
import requests
import json

def test_backend_connection():
    """Test if the backend is running and responding"""
    base_url = "http://localhost:8000"  # Using the corrected port
    
    print("🔍 Testing backend connection...")
    print(f"Base URL: {base_url}")
    
    # Test 1: Health check
    try:
        print("\n1️⃣ Testing health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Health data: {data}")
            print("✅ Health check passed!")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Is it running?")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Start chat session
    try:
        print("\n2️⃣ Testing chat session start...")
        response = requests.post(
            f"{base_url}/api/chat/start",
            headers={'Content-Type': 'application/json'},
            json={"user_id": "test-user"},
            timeout=5
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Session data: {data}")
            session_id = data.get('session_id')
            print("✅ Chat session creation passed!")
            return session_id
        else:
            print(f"❌ Chat session failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Chat session error: {e}")
        return False

def test_chat_message(session_id):
    """Test sending a simple message"""
    base_url = "http://localhost:8000"
    
    print("\n3️⃣ Testing chat message...")
    try:
        response = requests.post(
            f"{base_url}/api/chat/stream",
            headers={'Content-Type': 'application/json'},
            json={
                "session_id": session_id,
                "message": "Hello!"
            },
            stream=True,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Stream started successfully!")
            
            # Read a few lines to confirm streaming works
            lines_read = 0
            for line in response.iter_lines():
                if line and lines_read < 5:
                    decoded_line = line.decode('utf-8')
                    print(f"Stream line: {decoded_line[:100]}...")
                    lines_read += 1
                elif lines_read >= 5:
                    break
            print("✅ Streaming works!")
            return True
        else:
            print(f"❌ Stream failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Stream error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Backend Connection Test\n")
    
    session_id = test_backend_connection()
    if session_id:
        test_chat_message(session_id)
    
    print("\n" + "="*50)
    print("📝 Next Steps:")
    print("1. If tests pass: Restart your frontend (npm start)")
    print("2. If tests fail: Check that working_agent.py is running")
    print("3. Backend should be on: http://localhost:8000")
    print("4. Frontend should connect to: http://localhost:8000")
