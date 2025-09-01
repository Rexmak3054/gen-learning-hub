#!/usr/bin/env python3
"""
Test the fixed clean agent implementation
"""

import asyncio
import aiohttp
import json

async def test_fixed_clean_agent():
    """Test both fixes: course cards + clean responses"""
    
    base_url = "http://localhost:8001"
    
    print("🧪 Testing Fixed Clean Agent")
    print("=" * 40)
    
    try:
        async with aiohttp.ClientSession() as session:
            # Start session
            async with session.post(f"{base_url}/api/chat/start") as resp:
                data = await resp.json()
                session_id = data["session_id"]
                print(f"✅ Session: {session_id}")
            
            # Test 1: General question (should not trigger courses)
            print(f"\\n1. Testing General Question...")
            await test_message(session, base_url, session_id, "Hello, how are you?", expect_courses=False)
            
            # Test 2: Course request (should trigger courses)
            print(f"\\n2. Testing Course Request...")
            await test_message(session, base_url, session_id, "I want to learn Python programming", expect_courses=True)
            
            # Test 3: Follow-up (should remember context)
            print(f"\\n3. Testing Follow-up...")
            await test_message(session, base_url, session_id, "Tell me more about the first course", expect_courses=False)
            
            print(f"\\n🎉 All tests completed!")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

async def test_message(session, base_url, session_id, message, expect_courses=False):
    """Test a single message"""
    
    print(f"   Sending: '{message}'")
    
    assistant_responses = []
    course_data = None
    json_responses = 0  # Count responses that look like JSON
    
    async with session.post(
        f"{base_url}/api/chat/stream",
        json={"session_id": session_id, "message": message}
    ) as resp:
        
        async for line in resp.content:
            line_str = line.decode('utf-8').strip()
            
            if line_str.startswith('data: ') and len(line_str) > 6:
                try:
                    data = json.loads(line_str[6:])
                    event = data.get('event')
                    
                    if event == 'message_added' and data['data']['message_type'] == 'assistant':
                        content = data['data']['content']
                        assistant_responses.append(content)
                        
                        # Check if response looks like JSON data
                        if content.strip().startswith('{') and 'courses' in content:
                            json_responses += 1
                            print(f"   ⚠️ JSON response detected: {content[:50]}...")
                        else:
                            print(f"   🤖 Clean response: {content[:60]}...")
                    
                    elif event == 'courses_ready':
                        course_data = data['data']
                        course_count = len(course_data.get('courses', []))
                        print(f"   📚 Course cards ready: {course_count} courses")
                    
                    elif event == 'stream_complete':
                        break
                        
                except json.JSONDecodeError as e:
                    print(f"   ❌ Parse error: {e}")
    
    # Analysis
    print(f"   📊 Analysis:")
    print(f"      Assistant responses: {len(assistant_responses)}")
    print(f"      JSON responses (bad): {json_responses}")
    print(f"      Course data received: {'✅' if course_data else '❌'}")
    
    # Check expectations
    if expect_courses:
        if course_data:
            course_count = len(course_data.get('courses', []))
            print(f"      🎯 Expected courses: ✅ Got {course_count} courses")
        else:
            print(f"      🎯 Expected courses: ❌ No course data received")
    else:
        if course_data:
            print(f"      🎯 Unexpected courses: ⚠️ Got course data for general question")
        else:
            print(f"      🎯 No courses expected: ✅ Correct")
    
    if json_responses > 0:
        print(f"      ⚠️ ISSUE: {json_responses} JSON responses should be filtered out")
    else:
        print(f"      ✅ Clean responses: No JSON data in chat")

if __name__ == "__main__":
    print("🔍 This test verifies:")
    print("1. ✅ Course cards display properly")
    print("2. ✅ No JSON/tool results in chat responses") 
    print("3. ✅ General questions don't trigger courses")
    print("4. ✅ Course requests do trigger courses")
    print()
    print("Make sure clean agent is running: python clean_agent_chat.py")
    print()
    
    asyncio.run(test_fixed_clean_agent())
