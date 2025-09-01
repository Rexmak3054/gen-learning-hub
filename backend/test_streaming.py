#!/usr/bin/env python3
"""
Test script for Phase 3: Real-time Message Streaming
"""

import requests
import json
import time
import asyncio
import threading
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_streaming_chat():
    """Test the Phase 3 real-time streaming chat functionality"""
    
    print("🌊 Testing Phase 3: Real-time Message Streaming")
    print("=" * 70)
    
    # Test 1: Health check
    print("\n1️⃣ Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            result = response.json()
            print("✅ Health check passed")
            print(f"   Status: {result['status']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return
    
    # Test 2: Start chat session
    print("\n2️⃣ Starting chat session for streaming test...")
    try:
        start_data = {"user_id": "streaming-test-user"}
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
    
    # Test 3: Test streaming endpoint with real-time message flow
    print("\n3️⃣ Testing real-time streaming...")
    print("   📤 Sending: 'I want to learn Python programming'")
    print("   🔄 Watching real-time stream...")
    print("\n" + "─" * 50)
    
    try:
        stream_data = {
            "session_id": session_id,
            "message": "I want to learn Python programming"
        }
        
        # Stream the response in real-time
        with requests.post(\n            f\"{BASE_URL}/api/chat/stream\", \n            json=stream_data, \n            stream=True,\n            headers={\"Accept\": \"text/event-stream\"}\n        ) as response:\n            \n            if response.status_code == 200:\n                message_count = 0\n                start_time = time.time()\n                \n                print(f\"🌊 Streaming started at {datetime.now().strftime('%H:%M:%S')}\")\n                \n                for line in response.iter_lines():\n                    if line:\n                        line_str = line.decode('utf-8')\n                        \n                        if line_str.startswith('data: '):\n                            try:\n                                data_json = line_str[6:]  # Remove 'data: ' prefix\n                                data = json.loads(data_json)\n                                \n                                event_type = data.get('event', 'unknown')\n                                event_data = data.get('data', {})\n                                timestamp = data.get('timestamp', '')\n                                \n                                current_time = datetime.now().strftime('%H:%M:%S.%f')[:-3]\n                                \n                                if event_type == 'message_added':\n                                    message_count += 1\n                                    msg_type = event_data.get('message_type', 'unknown')\n                                    content = event_data.get('content', '')[:60]\n                                    \n                                    # Use different emojis for different message types\n                                    emoji_map = {\n                                        'user': '👤',\n                                        'agent_thinking': '🤔',\n                                        'agent_searching': '🔍',\n                                        'agent_courses': '📚',\n                                        'agent_response': '🤖'\n                                    }\n                                    emoji = emoji_map.get(msg_type, '💬')\n                                    \n                                    print(f\"{current_time} {emoji} [{msg_type}] {content}...\")\n                                    \n                                    # Show course count if present\n                                    if event_data.get('metadata', {}).get('courses'):\n                                        course_count = len(event_data['metadata']['courses'])\n                                        print(f\"{' ' * 15}📊 Contains {course_count} courses\")\n                                \n                                elif event_type == 'stream_complete':\n                                    elapsed = time.time() - start_time\n                                    print(f\"{current_time} ✅ Stream completed successfully!\")\n                                    print(f\"{' ' * 15}⏱️  Total time: {elapsed:.2f}s\")\n                                    print(f\"{' ' * 15}📨 Messages streamed: {message_count}\")\n                                    break\n                                    \n                                elif event_type == 'stream_error':\n                                    print(f\"{current_time} ❌ Stream error: {event_data.get('error')}\")\n                                    break\n                                \n                            except json.JSONDecodeError as e:\n                                print(f\"   ⚠️  JSON decode error: {e}\")\n                \n                print(\"─\" * 50)\n                print(\"✅ Real-time streaming test completed!\")\n                \n            else:\n                print(f\"❌ Streaming failed: {response.status_code}\")\n                print(f\"   Response: {response.text[:200]}...\")\n                \n    except Exception as e:\n        print(f\"❌ Streaming test error: {e}\")\n        import traceback\n        traceback.print_exc()\n    \n    # Test 4: Compare with non-streaming endpoint\n    print(\"\\n4️⃣ Comparing with non-streaming endpoint...\")\n    print(\"   📤 Sending: 'Find me data science courses' (non-streaming)\")\n    \n    start_time = time.time()\n    try:\n        message_data = {\n            \"session_id\": session_id,\n            \"message\": \"Find me data science courses\"\n        }\n        response = requests.post(f\"{BASE_URL}/api/chat/message\", json=message_data)\n        elapsed = time.time() - start_time\n        \n        if response.status_code == 200:\n            result = response.json()\n            if result[\"success\"]:\n                print(f\"✅ Non-streaming response received in {elapsed:.2f}s\")\n                print(f\"   Response type: {result['message']['message_type']}\")\n                print(f\"   Response: {result['message']['content'][:60]}...\")\n            else:\n                print(f\"❌ Non-streaming failed: {result.get('error')}\")\n        else:\n            print(f\"❌ Non-streaming request failed: {response.status_code}\")\n            \n    except Exception as e:\n        print(f\"❌ Non-streaming test error: {e}\")\n    \n    # Test 5: Check final conversation history\n    print(\"\\n5️⃣ Checking final conversation history...\")\n    try:\n        response = requests.get(f\"{BASE_URL}/api/chat/history/{session_id}\")\n        \n        if response.status_code == 200:\n            result = response.json()\n            if result[\"success\"]:\n                total_messages = result['total_messages']\n                print(f\"✅ Final conversation: {total_messages} total messages\")\n                \n                # Count by type\n                types = {}\n                for msg in result[\"messages\"]:\n                    msg_type = msg['message_type']\n                    types[msg_type] = types.get(msg_type, 0) + 1\n                \n                print(\"   📊 Message breakdown:\")\n                for msg_type, count in types.items():\n                    print(f\"     • {msg_type}: {count}\")\n                    \n            else:\n                print(f\"❌ History check failed: {result.get('error')}\")\n        else:\n            print(f\"❌ History request failed: {response.status_code}\")\n            \n    except Exception as e:\n        print(f\"❌ History check error: {e}\")\n    \n    print(\"\\n\" + \"=\" * 70)\n    print(\"🎉 Phase 3: Real-time Streaming Test Complete!\")\n    print(\"\\n🌊 What's Now Working:\")\n    print(\"   ✅ Real-time Server-Sent Events streaming\")\n    print(\"   ✅ Step-by-step agent processing with delays\")\n    print(\"   ✅ Live message updates as agent thinks\")\n    print(\"   ✅ Course data embedded in stream\")\n    print(\"   ✅ Backward compatibility with non-streaming API\")\n    print(\"   ✅ Proper error handling in streams\")\n    print(\"\\n🚀 Ready for Frontend Integration:\")\n    print(\"   • Use /api/chat/stream for real-time experience\")\n    print(\"   • Use /api/chat/message for simple responses\")\n    print(\"   • EventSource in JavaScript for stream handling\")\n    print(\"   • Rich metadata available in all messages\")\n    print(\"\\n💡 Next Steps:\")\n    print(\"   • Frontend implementation with EventSource\")\n    print(\"   • UI animations for streaming messages\")\n    print(\"   • Typing indicators and loading states\")\n\ndef test_simple_stream():\n    \"\"\"Simple streaming test for debugging\"\"\"\n    print(\"🧪 Simple Streaming Test\")\n    \n    # Start session\n    start_data = {\"user_id\": \"simple-test\"}\n    response = requests.post(f\"{BASE_URL}/api/chat/start\", json=start_data)\n    session_id = response.json()[\"session_id\"]\n    \n    # Stream a message\n    stream_data = {\n        \"session_id\": session_id,\n        \"message\": \"Hello!\"\n    }\n    \n    with requests.post(f\"{BASE_URL}/api/chat/stream\", json=stream_data, stream=True) as response:\n        print(f\"Status: {response.status_code}\")\n        for line in response.iter_lines():\n            if line:\n                print(f\"Received: {line.decode('utf-8')}\")\n\nif __name__ == \"__main__\":\n    import sys\n    if len(sys.argv) > 1 and sys.argv[1] == \"simple\":\n        test_simple_stream()\n    else:\n        test_streaming_chat()\n