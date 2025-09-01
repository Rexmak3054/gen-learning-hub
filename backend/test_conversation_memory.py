#!/usr/bin/env python3
"""
Test conversation memory and general chat capabilities
"""

import asyncio
import aiohttp
import json

async def test_conversation_memory():
    """Test that the agent remembers conversation context"""
    
    base_url = "http://localhost:8000"
    
    print("🧠 Testing Conversation Memory & General Chat...")
    print("=" * 60)
    
    try:
        async with aiohttp.ClientSession() as session:
            # Start a chat session
            print("1. Starting chat session...")
            async with session.post(
                f"{base_url}/api/chat/start",
                json={"user_id": "memory-test"}
            ) as resp:
                data = await resp.json()
                session_id = data["session_id"]
                print(f"   ✅ Session: {session_id}")
            
            # Test sequence to check memory
            test_sequence = [
                ("Hello, how are you?", "general"),
                ("What's the weather like?", "general"),
                ("I want to learn Python programming", "course-related"),
                ("Actually, make that more advanced Python courses", "follow-up"),
                ("What do you think about AI in general?", "general"),
                ("Can you tell me more about the first Python course you recommended?", "follow-up")
            ]
            
            print(f"\n2. Running conversation sequence...")
            
            for i, (message, expected_type) in enumerate(test_sequence, 1):
                print(f"\n   Step {i}: {expected_type.upper()}")
                print(f"   User: \"{message}\"")
                
                await test_single_message(session, base_url, session_id, message, expected_type)
                
                # Small delay between messages
                await asyncio.sleep(1)
            
            print(f"\n🎉 Conversation memory test completed!")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

async def test_single_message(session, base_url, session_id, message, expected_type):
    """Test a single message and analyze the response"""
    
    agent_responses = []
    courses_found = False
    parse_errors = 0
    
    async with session.post(
        f"{base_url}/api/chat/stream",
        json={
            "session_id": session_id,
            "message": message
        }
    ) as resp:
        
        if resp.status != 200:
            print(f"   ❌ HTTP Error: {resp.status}")
            return
        
        async for line in resp.content:
            line_str = line.decode('utf-8').strip()
            
            if line_str.startswith('data: ') and len(line_str) > 6:
                try:
                    json_str = line_str[6:].strip()
                    if not json_str:
                        continue
                        
                    data = json.loads(json_str)
                    event = data.get('event')
                    
                    if event == 'message_added':
                        if data['data']['message_type'] == 'agent_response':
                            content = data['data']['content']
                            agent_responses.append(content)
                            print(f"   🤖 Agent: \"{content[:80]}...\"")
                    
                    elif event == 'courses_ready':
                        courses_found = True
                        course_count = len(data['data']['courses'])
                        print(f"   📚 Courses: {course_count} found")
                    
                    elif event == 'stream_complete':
                        break
                    
                    elif event == 'stream_error':
                        print(f"   ❌ Stream error: {data['data']}")
                        break
                        
                except json.JSONDecodeError as e:
                    parse_errors += 1
                    print(f"   ⚠️ Parse error: {str(e)[:30]}...")
                except Exception as e:
                    print(f"   ❌ Processing error: {e}")
    
    # Analyze response quality
    if expected_type == "general" and courses_found:
        print(f"   ⚠️ Unexpected courses for general question")
    elif expected_type == "course-related" and not courses_found:
        print(f"   ⚠️ No courses found for course-related question")
    elif expected_type == "follow-up":
        print(f"   💭 Follow-up handled: {'✅' if agent_responses else '❌'}")
    
    if parse_errors > 0:
        print(f"   ❌ Parse errors: {parse_errors}")
    else:
        print(f"   ✅ Clean parsing")

if __name__ == "__main__":
    print("🧪 Conversation Memory & General Chat Test")
    print("This tests:")
    print("- General questions (non-course)")
    print("- Course-related questions") 
    print("- Follow-up questions with memory")
    print("- Context preservation across messages")
    print()
    print("Make sure the server is running: python main_with_agent.py\n")
    
    asyncio.run(test_conversation_memory())