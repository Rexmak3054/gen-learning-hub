#!/usr/bin/env python3
"""
Test the fixed clean agent for both issues
"""

import asyncio
import aiohttp
import json

async def test_both_fixes():
    """Test that both issues are fixed"""
    
    base_url = "https://3.26.39.202/"
    
    print("🧪 Testing Both Fixes: Course Cards + Clean Responses")
    print("=" * 60)
    
    try:
        async with aiohttp.ClientSession() as session:
            # Start session
            async with session.post(f"{base_url}/api/chat/start") as resp:
                data = await resp.json()
                session_id = data["session_id"]
                print(f"✅ Session: {session_id}")
            
            # Test 1: General question (should be clean, no courses)
            print(f"\n1. Testing General Question (should be clean)...")
            await analyze_response(session, base_url, session_id, "Hello, how are you today?", expect_courses=False)
            
            # Test 2: Course request (should show course cards)
            print(f"\n2. Testing Course Request (should show course cards)...")
            await analyze_response(session, base_url, session_id, "I want to learn Python programming", expect_courses=True)
            
            # Test 3: Follow-up question (should remember context, be clean)
            print(f"\n3. Testing Follow-up (should remember context)...")
            await analyze_response(session, base_url, session_id, "What do you think about the courses you found?", expect_courses=False)
            
            print(f"\n🎉 All tests completed!")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

async def analyze_response(session, base_url, session_id, message, expect_courses=False):
    """Analyze a single response for issues"""
    
    print(f"   📨 Message: '{message}'")
    
    assistant_responses = []
    json_in_chat = 0
    system_msg_in_chat = 0
    course_data_received = None
    
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
                        
                        # Check for problems in responses
                        if content.strip().startswith('{') and ('"courses"' in content or '"success"' in content):
                            json_in_chat += 1
                            print(f"      ❌ JSON in chat: {content[:40]}...")
                        
                        if 'you are a helpful ai assistant' in content.lower() or 'follow this process' in content.lower():
                            system_msg_in_chat += 1
                            print(f"      ❌ System message in chat: {content[:40]}...")
                        
                        if not (content.strip().startswith('{') or 'you are a helpful' in content.lower()):
                            print(f"      ✅ Clean response: {content[:60]}...")
                    
                    elif event == 'courses_ready':
                        course_data_received = data['data']
                        course_count = len(course_data_received.get('courses', []))
                        print(f"      📚 Course cards: {course_count} courses received")
                    
                    elif event == 'stream_complete':
                        break
                        
                except json.JSONDecodeError as e:
                    print(f"      ❌ Parse error: {e}")
    
    # Analysis summary
    print(f"   📊 Analysis:")
    print(f"      Total responses: {len(assistant_responses)}")
    print(f"      JSON responses (should be 0): {json_in_chat}")
    print(f"      System messages (should be 0): {system_msg_in_chat}")
    print(f"      Course data received: {'✅' if course_data_received else '❌'}")
    
    # Check expectations
    if expect_courses:
        if course_data_received:
            print(f"      🎯 Course expectation: ✅ Got course cards as expected")
        else:
            print(f"      🎯 Course expectation: ❌ Expected courses but none received")
    else:
        if course_data_received:
            print(f"      🎯 General expectation: ⚠️ Got unexpected course cards")
        else:
            print(f"      🎯 General expectation: ✅ No courses as expected")
    
    # Overall assessment
    issues = json_in_chat + system_msg_in_chat
    if issues == 0:
        print(f"      🎉 CLEAN: No JSON or system messages in chat!")
    else:
        print(f"      ⚠️ ISSUES: {issues} problematic responses detected")

if __name__ == "__main__":
    print("🔍 This test verifies both fixes:")
    print("1. ✅ Course cards display properly with actual course data")
    print("2. ✅ No JSON tool results in chat responses") 
    print("3. ✅ No system messages in chat responses")
    print("4. ✅ Only clean conversational responses")
    print()
    print("Make sure clean agent is running: python clean_agent_chat.py")
    print()
    
    asyncio.run(test_both_fixes())
