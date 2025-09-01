#!/usr/bin/env python3
"""
Quick test script for the improved streaming chat
"""

import asyncio
import json
from datetime import datetime

async def test_streaming_demo():
    """Test the streaming endpoints"""
    import aiohttp
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Improved Streaming Chat...")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test health endpoint
            print("1. Testing health endpoint...")
            async with session.get(f"{base_url}/health") as resp:
                if resp.status == 200:
                    print("   ✅ Health check passed")
                else:
                    print(f"   ❌ Health check failed: {resp.status}")
                    return
            
            # Start a chat session
            print("2. Starting chat session...")
            async with session.post(
                f"{base_url}/api/chat/start",
                json={"user_id": "test-user"}
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data["success"]:
                        session_id = data["session_id"]
                        print(f"   ✅ Chat session started: {session_id}")
                    else:
                        print(f"   ❌ Failed to start session: {data}")
                        return
                else:
                    print(f"   ❌ Failed to start session: {resp.status}")
                    return
            
            # Test streaming
            print("3. Testing streaming chat...")
            async with session.post(
                f"{base_url}/api/chat/stream",
                json={
                    "session_id": session_id,
                    "message": "I want to learn Python programming"
                }
            ) as resp:
                if resp.status == 200:
                    print("   ✅ Streaming started")
                    
                    message_count = 0
                    courses_received = False
                    
                    async for line in resp.content:
                        line_str = line.decode('utf-8').strip()
                        if line_str.startswith('data: '):
                            try:
                                data = json.loads(line_str[6:])
                                event = data.get('event')
                                
                                if event == 'message_added':
                                    message_count += 1
                                    msg_type = data['data']['message_type']
                                    content = data['data']['content'][:50] + "..."
                                    print(f"   📝 Message ({msg_type}): {content}")
                                
                                elif event == 'courses_ready':
                                    courses_received = True
                                    course_count = len(data['data']['courses'])
                                    query = data['data']['query']
                                    is_update = data['data'].get('is_update', False)
                                    print(f"   📚 Courses ready: {course_count} courses for '{query}' (update: {is_update})")
                                
                                elif event == 'stream_complete':
                                    print("   ✅ Stream completed successfully")
                                    break
                                
                                elif event == 'stream_error':
                                    print(f"   ❌ Stream error: {data['data']}")
                                    break
                                    
                            except json.JSONDecodeError as e:
                                print(f"   ⚠️ JSON decode error: {e}")
                    
                    print(f"\n📊 Test Results:")
                    print(f"   Messages received: {message_count}")
                    print(f"   Courses received: {'Yes' if courses_received else 'No'}")
                    
                else:
                    print(f"   ❌ Streaming failed: {resp.status}")
            
            print("\n🎉 Test completed!")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Make sure the backend server is running on http://localhost:8000")
    print("Start it with: cd backend && python main_with_agent.py")
    print()
    
    asyncio.run(test_streaming_demo())