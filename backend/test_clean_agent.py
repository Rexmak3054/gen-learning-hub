#!/usr/bin/env python3
"""
Test the clean agent chat implementation
"""

import asyncio
import aiohttp
import json

async def test_clean_agent():
    """Test the clean agent implementation"""
    
    base_url = "http://localhost:8001"
    
    print("🧪 Testing Clean Agent Chat Implementation")
    print("=" * 50)
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test health
            print("1. Testing health endpoint...")
            async with session.get(f"{base_url}/health") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"   ✅ Health: {data['status']}")
                    print(f"   Agent initialized: {data['agent_initialized']}")
                    print(f"   Tools loaded: {data['tools_loaded']}")
                else:
                    print(f"   ❌ Health check failed: {resp.status}")
                    return
            
            # Start chat session
            print("\\n2. Starting chat session...")
            async with session.post(f"{base_url}/api/chat/start") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    session_id = data["session_id"]
                    print(f"   ✅ Session created: {session_id}")
                else:
                    print(f"   ❌ Failed to create session: {resp.status}")
                    return
            
            # Test conversation flow
            test_messages = [
                ("Hello!", "Should get natural greeting"),
                ("I want to learn Python programming", "Should offer courses + trigger tool call"),
                ("What do you think about AI?", "Should discuss AI naturally"),
                ("Tell me more about those Python courses", "Should reference previous context")
            ]
            
            print("\\n3. Testing conversation flow...")
            
            for i, (message, expectation) in enumerate(test_messages, 1):
                print(f"\\n   Test {i}: \"{message}\"")
                print(f"   Expected: {expectation}")
                
                agent_responses = 0
                tool_calls_detected = 0
                courses_ready = False
                
                async with session.post(
                    f"{base_url}/api/chat/stream",
                    json={"session_id": session_id, "message": message}
                ) as resp:
                    
                    if resp.status != 200:
                        print(f"   ❌ Stream failed: {resp.status}")
                        continue
                    
                    async for line in resp.content:
                        line_str = line.decode('utf-8').strip()
                        
                        if line_str.startswith('data: ') and len(line_str) > 6:
                            try:
                                data = json.loads(line_str[6:])
                                event = data.get('event')
                                
                                if event == 'message_added':
                                    if data['data']['message_type'] == 'assistant':
                                        content = data['data']['content']
                                        agent_responses += 1
                                        print(f"   🤖 Agent: {content[:60]}...")
                                
                                elif event == 'courses_ready':
                                    courses_ready = True
                                    course_count = len(data['data'].get('course_uuids', []))
                                    print(f"   📚 Courses ready: {course_count} UUIDs")
                                    print(f"   🎯 Tool call detected successfully!")
                                
                                elif event == 'stream_complete':
                                    print(f"   ✅ Stream completed")
                                    break
                                
                                elif event == 'stream_error':
                                    print(f"   ❌ Stream error: {data['data']}")
                                    break
                                    
                            except json.JSONDecodeError as e:
                                print(f"   ⚠️ Parse error: {e}")
                
                # Analyze results
                print(f"   📊 Results:")
                print(f"      Agent responses: {agent_responses}")
                print(f"      Courses triggered: {'✅' if courses_ready else '❌'}")
                
                # Small delay between messages
                await asyncio.sleep(1)
            
            print(f"\\n🎉 Clean agent test completed!")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 Clean Agent Chat Test")
    print("This tests the simplified agent architecture:")
    print("- Natural conversation with LangGraph")
    print("- Tool call detection for course recommendations") 
    print("- Clean streaming without artificial messages")
    print("- Conversation memory through LangChain")
    print()
    print("Make sure to start the server first:")
    print("cd backend && python clean_agent_chat.py")
    print()
    
    asyncio.run(test_clean_agent())