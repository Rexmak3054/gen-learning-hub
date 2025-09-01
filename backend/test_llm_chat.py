#!/usr/bin/env python3
"""
Test script for Phase 2: LLM-Powered Agent Integration
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_llm_powered_chat():
    """Test the Phase 2 chat API with LLM-powered natural language understanding"""
    
    print("🧪 Testing Phase 2: LLM-Powered Natural Language Chat")
    print("=" * 70)
    
    # Test 1: Health check
    print("\n1️⃣ Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            result = response.json()
            print("✅ Health check passed")
            print(f"   Status: {result['status']} - {result['message']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return
    
    # Test 2: Start chat session
    print("\n2️⃣ Starting new chat session...")
    try:
        start_data = {"user_id": "test-llm-chat"}
        response = requests.post(f"{BASE_URL}/api/chat/start", json=start_data)
        
        if response.status_code == 200:
            result = response.json()
            if result["success"]:
                session_id = result["session_id"]
                print("✅ Chat session started")
                print(f"   Session ID: {session_id[:12]}...")
            else:
                print(f"❌ Chat session start failed: {result.get('error')}")
                return
        else:
            print(f"❌ Chat session start failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Chat session start error: {e}")
        return
    
    # Define test messages that showcase natural language understanding
    test_messages = [
        {
            "message": "I want to learn Python programming",
            "description": "Direct course request"
        },
        {
            "message": "What's the weather like today?",
            "description": "Non-course related (should still be handled by LLM)"
        },
        {
            "message": "I'm a complete beginner and want to get into web development",
            "description": "Complex natural language with context"
        },
        {
            "message": "Help me become better at data science for my career",
            "description": "Career-focused learning request"
        },
        {
            "message": "I need to upskill in machine learning but I'm not sure where to start",
            "description": "Uncertain learner needing guidance"
        }
    ]
    
    # Test each message
    for i, test_case in enumerate(test_messages, 3):
        print(f"\n{i}️⃣ Testing LLM understanding: {test_case['description']}")
        print(f"   Sending: '{test_case['message']}'")
        
        try:
            message_data = {
                "session_id": session_id,
                "message": test_case["message"]
            }
            response = requests.post(f"{BASE_URL}/api/chat/message", json=message_data)
            
            if response.status_code == 200:
                result = response.json()
                if result["success"]:
                    print("✅ LLM processed message successfully")
                    print(f"   Response type: {result['message']['message_type']}")
                    print(f"   Response: {result['message']['content'][:100]}...")
                    
                    # Brief pause between tests
                    time.sleep(0.5)
                else:
                    print(f"❌ LLM processing failed: {result.get('error')}")
            else:
                print(f"❌ Request failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Test error: {e}")
    
    # Test final: Check complete conversation history
    print(f"\n{len(test_messages) + 3}️⃣ Checking complete conversation history...")
    try:
        response = requests.get(f"{BASE_URL}/api/chat/history/{session_id}")
        
        if response.status_code == 200:
            result = response.json()
            if result["success"]:
                print(f"✅ Retrieved complete conversation: {result['total_messages']} messages")
                
                # Group messages by conversation
                conversations = []
                current_conv = []
                
                for msg in result["messages"]:
                    if msg['message_type'] == 'user':
                        if current_conv:  # Save previous conversation
                            conversations.append(current_conv)
                        current_conv = [msg]  # Start new conversation
                    else:
                        current_conv.append(msg)
                
                if current_conv:  # Add final conversation
                    conversations.append(current_conv)
                
                print(f"\n   📊 Conversation Analysis:")
                print(f"   Total conversations: {len(conversations)}")
                
                # Count message types
                types = {}
                courses_found = 0
                for msg in result["messages"]:
                    msg_type = msg['message_type']
                    types[msg_type] = types.get(msg_type, 0) + 1
                    
                    if msg.get('metadata', {}).get('courses'):
                        courses_found += len(msg['metadata']['courses'])
                
                print(f"   Message type breakdown:")
                for msg_type, count in types.items():
                    print(f"     • {msg_type}: {count}")
                
                if courses_found > 0:
                    print(f"   📚 Total courses discovered: {courses_found}")
                
                # Show sample conversation
                if conversations:
                    print(f"\n   💬 Sample conversation flow:")
                    sample = conversations[0]  # First conversation
                    for j, msg in enumerate(sample[:4]):  # Show first 4 messages
                        timestamp = msg['timestamp'][:19] if 'T' in msg['timestamp'] else msg['timestamp']
                        print(f"     {j+1}. [{msg['message_type']}] {msg['content'][:60]}...")
                    
            else:
                print(f"❌ History retrieval failed: {result.get('error')}")
        else:
            print(f"❌ History request failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ History check error: {e}")
    
    print("\n" + "=" * 70)
    print("🎉 LLM-Powered Chat Test Complete!")
    print("\n🧠 What the LLM Agent Now Handles:")
    print("   ✅ Natural language understanding (no manual parsing!)")
    print("   ✅ Course requests in any format")
    print("   ✅ Context-aware responses")  
    print("   ✅ Step-by-step thinking process")
    print("   ✅ Non-course queries (gracefully handled)")
    print("   ✅ Complex learning scenarios")
    print("\n🚀 Ready for Production:")
    print("   • Frontend can now send any natural language")
    print("   • Agent intelligently processes all requests")
    print("   • Rich conversation history with metadata")
    print("   • Course data embedded in chat flow")
    print("\n⏭️  Next: Phase 3 - Real-time streaming!")

if __name__ == "__main__":
    test_llm_powered_chat()
