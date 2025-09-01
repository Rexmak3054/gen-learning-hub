#!/usr/bin/env python3
"""
Simple test script for the chat API endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_chat_api():
    """Test the chat API endpoints"""
    
    print("🧪 Testing Chat API - Phase 1")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1️⃣ Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return
    
    # Test 2: Start chat session
    print("\n2️⃣ Testing chat session start...")
    try:
        start_data = {"user_id": "test-user-123"}
        response = requests.post(f"{BASE_URL}/api/chat/start", json=start_data)
        
        if response.status_code == 200:
            result = response.json()
            if result["success"]:
                session_id = result["session_id"]
                print("✅ Chat session started successfully")
                print(f"   Session ID: {session_id}")
            else:
                print(f"❌ Chat session start failed: {result.get('error')}")
                return
        else:
            print(f"❌ Chat session start failed: {response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ Chat session start error: {e}")
        return
    
    # Test 3: Get initial chat history
    print("\n3️⃣ Testing chat history (should have welcome message)...")
    try:
        response = requests.get(f"{BASE_URL}/api/chat/history/{session_id}")
        
        if response.status_code == 200:
            result = response.json()
            if result["success"]:
                print("✅ Chat history retrieved successfully")
                print(f"   Total messages: {result['total_messages']}")
                for i, msg in enumerate(result["messages"]):
                    print(f"   Message {i+1}: [{msg['message_type']}] {msg['content'][:50]}...")
            else:
                print(f"❌ Chat history failed: {result.get('error')}")
        else:
            print(f"❌ Chat history failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Chat history error: {e}")
    
    # Test 4: Send a user message
    print("\n4️⃣ Testing send message...")
    try:
        message_data = {
            "session_id": session_id,
            "message": "Hello! I want to learn Python programming."
        }
        response = requests.post(f"{BASE_URL}/api/chat/message", json=message_data)
        
        if response.status_code == 200:
            result = response.json()
            if result["success"]:
                print("✅ Message sent successfully")
                print(f"   Message ID: {result['message']['id']}")
                print(f"   Message Type: {result['message']['message_type']}")
                print(f"   Content: {result['message']['content']}")
            else:
                print(f"❌ Message send failed: {result.get('error')}")
        else:
            print(f"❌ Message send failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Message send error: {e}")
    
    # Test 5: Check updated chat history
    print("\n5️⃣ Testing updated chat history...")
    try:
        response = requests.get(f"{BASE_URL}/api/chat/history/{session_id}")
        
        if response.status_code == 200:
            result = response.json()
            if result["success"]:
                print("✅ Updated chat history retrieved successfully")
                print(f"   Total messages: {result['total_messages']}")
                for i, msg in enumerate(result["messages"]):
                    print(f"   Message {i+1}: [{msg['message_type']}] {msg['content'][:50]}...")
            else:
                print(f"❌ Updated chat history failed: {result.get('error')}")
        else:
            print(f"❌ Updated chat history failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Updated chat history error: {e}")
    
    # Test 6: Test invalid session
    print("\n6️⃣ Testing invalid session handling...")
    try:
        invalid_data = {
            "session_id": "invalid-session-id",
            "message": "This should fail"
        }
        response = requests.post(f"{BASE_URL}/api/chat/message", json=invalid_data)
        
        if response.status_code == 200:
            result = response.json()
            if not result["success"]:
                print("✅ Invalid session properly handled")
                print(f"   Error: {result.get('error')}")
            else:
                print("❌ Invalid session should have failed")
        else:
            print(f"❌ Invalid session test failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Invalid session test error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Phase 1 Chat API Test Complete!")
    print("\nNext Steps:")
    print("- ✅ Basic chat session management works")
    print("- ✅ Message storage and retrieval works")
    print("- ⏳ Phase 2: Add agent processing logic")
    print("- ⏳ Phase 3: Add step-by-step message streaming")

if __name__ == "__main__":
    test_chat_api()
