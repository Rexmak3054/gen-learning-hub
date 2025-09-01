#!/usr/bin/env python3
"""
Test the improved clean agent with course detection
"""

import asyncio
import aiohttp
import json

async def test_course_detection():
    """Test that course detection works"""
    
    base_url = "http://localhost:8001"
    
    print("🧪 Testing Course Detection in Clean Agent")
    print("=" * 50)
    
    try:
        async with aiohttp.ClientSession() as session:
            # Start session
            async with session.post(f"{base_url}/api/chat/start") as resp:
                data = await resp.json()
                session_id = data["session_id"]
                print(f"✅ Session: {session_id}")
            
            # Test course request
            print(f"\\n🎯 Testing: 'I want to learn Python programming'")
            
            agent_responses = []
            course_events = []
            tool_calls_seen = []
            
            async with session.post(
                f"{base_url}/api/chat/stream",
                json={"session_id": session_id, "message": "I want to learn Python programming"}
            ) as resp:
                
                async for line in resp.content:
                    line_str = line.decode('utf-8').strip()
                    
                    if line_str.startswith('data: ') and len(line_str) > 6:
                        try:
                            data = json.loads(line_str[6:])
                            event = data.get('event')
                            
                            if event == 'message_added':
                                msg_type = data['data']['message_type']
                                content = data['data']['content']
                                
                                if msg_type == 'assistant':
                                    agent_responses.append(content)
                                    print(f"🤖 Agent: {content[:80]}...")
                                    
                                    # Check if response contains tool calls or course data
                                    if 'course' in content.lower() or 'python' in content.lower():
                                        print(f"   💡 Response mentions courses/Python")
                            
                            elif event == 'courses_ready':
                                course_events.append(data['data'])
                                course_count = len(data['data'].get('course_uuids', []))
                                source = data['data'].get('source', 'unknown')
                                print(f"📚 COURSES READY: {course_count} courses from {source}")
                                print(f"   UUIDs: {data['data'].get('course_uuids', [])[:2]}...")
                            
                            elif event == 'stream_complete':
                                print(f"✅ Stream completed")
                                break
                                
                        except json.JSONDecodeError as e:
                            print(f"❌ Parse error: {e}")
            
            # Results summary
            print(f"\\n📊 Results Summary:")
            print(f"   Agent responses: {len(agent_responses)}")
            print(f"   Course events: {len(course_events)}")
            
            if course_events:
                print(f"   🎉 SUCCESS: Course detection working!")
                for i, event in enumerate(course_events):
                    print(f"      Event {i+1}: {len(event.get('course_uuids', []))} UUIDs from {event.get('source')}")
            else:
                print(f"   ❌ FAILED: No course events detected")
                print(f"   💡 Check if agent is using course tools in responses")
            
            # Test general message to ensure it doesn't trigger courses
            print(f"\\n🧪 Testing General Message: 'What is the weather today?'")
            
            general_course_events = 0
            
            async with session.post(
                f"{base_url}/api/chat/stream",
                json={"session_id": session_id, "message": "What is the weather today?"}
            ) as resp:
                
                async for line in resp.content:
                    line_str = line.decode('utf-8').strip()
                    
                    if line_str.startswith('data: ') and len(line_str) > 6:
                        try:
                            data = json.loads(line_str[6:])
                            
                            if data.get('event') == 'courses_ready':
                                general_course_events += 1
                                print(f"   ⚠️ Unexpected course event for general question")
                            
                            elif data.get('event') == 'message_added' and data['data']['message_type'] == 'assistant':
                                content = data['data']['content']
                                print(f"   🤖 General response: {content[:60]}...")
                            
                            elif data.get('event') == 'stream_complete':
                                break
                                
                        except json.JSONDecodeError:
                            pass
            
            if general_course_events == 0:
                print(f"   ✅ Good: No course events for general question")
            else:
                print(f"   ❌ Problem: {general_course_events} unexpected course events")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔍 This test verifies course detection works correctly")
    print("Expected:")
    print("- Course questions → trigger course events")  
    print("- General questions → no course events")
    print("- Clean JSON parsing throughout")
    print()
    print("Make sure clean agent is running: python clean_agent_chat.py")
    print()
    
    asyncio.run(test_course_detection())
