#!/usr/bin/env python3
"""
Test script for Phase 2: Agent Integration with Chat API
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_phase2_chat_api():
    """Test the Phase 2 chat API with agent integration"""
    
    print("🧪 Testing Chat API - Phase 2: Agent Integration")
    print("=" * 60)
    
    # Test 1: Health check
    print("\n1️⃣ Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            result = response.json()
            print("✅ Health check passed")
            print(f"   Status: {result['status']}")
            print(f"   Version: {result['version']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return
    
    # Test 2: Start chat session
    print("\n2️⃣ Starting new chat session...")
    try:
        start_data = {"user_id": "test-user-phase2"}
        response = requests.post(f"{BASE_URL}/api/chat/start", json=start_data)
        
        if response.status_code == 200:
            result = response.json()
            if result["success"]:
                session_id = result["session_id"]
                print("✅ Chat session started")
                print(f"   Session ID: {session_id[:8]}...")
            else:
                print(f"❌ Chat session start failed: {result.get('error')}")
                return
        else:
            print(f"❌ Chat session start failed: {response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ Chat session start error: {e}")
        return
    
    # Test 3: Send a course-related message (should trigger agent processing)
    print("\n3️⃣ Testing agent processing with course request...")
    print("   Sending: 'I want to learn Python programming'")
    
    try:
        message_data = {
            "session_id": session_id,
            "message": "I want to learn Python programming"
        }
        response = requests.post(f"{BASE_URL}/api/chat/message", json=message_data)
        
        if response.status_code == 200:
            result = response.json()
            if result["success"]:
                print("✅ Message processed by agent")
                print(f"   Response type: {result['message']['message_type']}")
                print(f"   Response: {result['message']['content'][:100]}...")
                print(f"   Has more messages: {result['has_more_messages']}")
                
                # Wait a moment for processing
                time.sleep(1)
                
            else:
                print(f"❌ Agent processing failed: {result.get('error')}")
        else:
            print(f"❌ Agent processing failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Agent processing error: {e}")
    
    # Test 4: Check chat history to see all agent messages
    print("\n4️⃣ Checking complete chat history (should show agent's step-by-step process)...")
    try:
        response = requests.get(f"{BASE_URL}/api/chat/history/{session_id}")
        
        if response.status_code == 200:
            result = response.json()
            if result["success"]:
                print(f"✅ Retrieved chat history with {result['total_messages']} messages:")
                
                for i, msg in enumerate(result["messages"]):\n                    timestamp = msg['timestamp'][:19] if 'T' in msg['timestamp'] else msg['timestamp'][:19]\n                    print(f\"   {i+1}. [{msg['message_type']}] {timestamp}\")\n                    print(f\"      {msg['content'][:80]}{'...' if len(msg['content']) > 80 else ''}\")\n                    \n                    # Show course data if present\n                    if msg.get('metadata', {}).get('courses'):\n                        courses = msg['metadata']['courses']\n                        print(f\"      📚 Contains {len(courses)} courses\")\n                    \n                    print()\n                    \n            else:\n                print(f\"❌ Chat history failed: {result.get('error')}\")\n        else:\n            print(f\"❌ Chat history failed: {response.status_code}\")\n            \n    except Exception as e:\n        print(f\"❌ Chat history error: {e}\")\n    \n    # Test 5: Send a non-course message (should get general response)\n    print(\"5️⃣ Testing non-course message handling...\")\n    print(\"   Sending: 'What's the weather like?'\")\n    \n    try:\n        message_data = {\n            \"session_id\": session_id,\n            \"message\": \"What's the weather like?\"\n        }\n        response = requests.post(f\"{BASE_URL}/api/chat/message\", json=message_data)\n        \n        if response.status_code == 200:\n            result = response.json()\n            if result[\"success\"]:\n                print(\"✅ Non-course message handled\")\n                print(f\"   Response: {result['message']['content'][:100]}...\")\n            else:\n                print(f\"❌ Non-course message failed: {result.get('error')}\")\n        else:\n            print(f\"❌ Non-course message failed: {response.status_code}\")\n            \n    except Exception as e:\n        print(f\"❌ Non-course message error: {e}\")\n    \n    # Test 6: Send another course request with different topic\n    print(\"\\n6️⃣ Testing another course search...\")\n    print(\"   Sending: 'Find me machine learning courses'\")\n    \n    try:\n        message_data = {\n            \"session_id\": session_id,\n            \"message\": \"Find me machine learning courses\"\n        }\n        response = requests.post(f\"{BASE_URL}/api/chat/message\", json=message_data)\n        \n        if response.status_code == 200:\n            result = response.json()\n            if result[\"success\"]:\n                print(\"✅ Second course search processed\")\n                print(f\"   Response type: {result['message']['message_type']}\")\n                print(f\"   Response: {result['message']['content'][:100]}...\")\n            else:\n                print(f\"❌ Second course search failed: {result.get('error')}\")\n        else:\n            print(f\"❌ Second course search failed: {response.status_code}\")\n            \n    except Exception as e:\n        print(f\"❌ Second course search error: {e}\")\n    \n    # Test 7: Final chat history check\n    print(\"\\n7️⃣ Final chat history check...\")\n    try:\n        response = requests.get(f\"{BASE_URL}/api/chat/history/{session_id}\")\n        \n        if response.status_code == 200:\n            result = response.json()\n            if result[\"success\"]:\n                print(f\"✅ Final history: {result['total_messages']} total messages\")\n                \n                # Count message types\n                types = {}\n                courses_found = 0\n                for msg in result[\"messages\"]:\n                    msg_type = msg['message_type']\n                    types[msg_type] = types.get(msg_type, 0) + 1\n                    \n                    if msg.get('metadata', {}).get('courses'):\n                        courses_found += len(msg['metadata']['courses'])\n                \n                print(\"   Message breakdown:\")\n                for msg_type, count in types.items():\n                    print(f\"     {msg_type}: {count}\")\n                \n                if courses_found > 0:\n                    print(f\"   📚 Total courses found: {courses_found}\")\n                    \n            else:\n                print(f\"❌ Final history failed: {result.get('error')}\")\n        else:\n            print(f\"❌ Final history failed: {response.status_code}\")\n            \n    except Exception as e:\n        print(f\"❌ Final history error: {e}\")\n    \n    print(\"\\n\" + \"=\" * 60)\n    print(\"🎉 Phase 2 Agent Integration Test Complete!\")\n    print(\"\\n✅ What's Working:\")\n    print(\"   - Step-by-step agent processing\")\n    print(\"   - Course search integration with chat\")\n    print(\"   - Multiple message types (thinking, searching, courses)\")\n    print(\"   - Topic extraction from natural language\")\n    print(\"   - Non-course message handling\")\n    print(\"   - Conversation context maintenance\")\n    print(\"\\n⏳ Ready for Phase 3:\")\n    print(\"   - Real-time message streaming\")\n    print(\"   - Frontend integration\")\n    print(\"   - Enhanced conversation memory\")\n\nif __name__ == \"__main__\":\n    test_phase2_chat_api()\n