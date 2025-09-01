#!/usr/bin/env python3
"""
Comprehensive test for all the fixes
"""

import asyncio
import aiohttp
import json

async def test_all_fixes():
    """Test all the fixes: JSON parsing, user echo prevention, and course cards"""
    
    base_url = "http://localhost:8000"
    
    print("🔧 Testing All Chat Fixes...")
    print("=" * 50)
    
    try:
        async with aiohttp.ClientSession() as session:
            # Start a chat session
            print("1. Starting chat session...")
            async with session.post(
                f"{base_url}/api/chat/start",
                json={"user_id": "comprehensive-test"}
            ) as resp:
                data = await resp.json()
                session_id = data["session_id"]
                print(f"   ✅ Session: {session_id}")
            
            # Test the business analyst query that was failing
            print("\n2. Testing business analyst query (the problematic one)...")
            test_message = "I am a business analyst, i want to learn about how to use AI to create business report"
            
            await test_single_query(session, base_url, session_id, test_message)
            
            # Test another query to check for echo prevention
            print("\n3. Testing simple query to check echo prevention...")
            simple_message = "I want to learn Python programming"
            
            await test_single_query(session, base_url, session_id, simple_message)
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

async def test_single_query(session, base_url, session_id, message):
    """Test a single query and analyze the results"""
    
    print(f"   📤 Sending: '{message[:50]}...'")
    
    # Counters for analysis
    user_echoes = 0
    json_responses = 0
    clean_messages = 0
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
                        content = data['data']['content']
                        msg_type = data['data']['message_type']
                        
                        if msg_type == 'user':
                            continue
                        
                        # Check for user echo
                        is_echo = is_user_message_echo(content, message)
                        if is_echo:
                            user_echoes += 1
                            print(f"   🔁 ECHO DETECTED: {content[:40]}...")
                        
                        # Check for JSON response
                        is_json = is_json_content(content)
                        if is_json:
                            json_responses += 1
                            print(f"   📄 JSON DETECTED: {len(content)} chars")
                        
                        if not is_echo and not is_json:
                            clean_messages += 1
                            print(f"   💬 Clean message: {content[:60]}...")
                    
                    elif event == 'courses_ready':
                        courses_found = True
                        course_count = len(data['data']['courses'])
                        query = data['data']['query']
                        print(f"   🎯 COURSES READY: {course_count} courses")
                        
                        # Check first course structure
                        if data['data']['courses']:
                            first_course = data['data']['courses'][0]
                            print(f"   📝 Sample course: {first_course.get('title', 'No title')}")
                            print(f"   🏫 Provider: {first_course.get('partner_primary', first_course.get('provider', 'Unknown'))}")
                    
                    elif event == 'stream_complete':
                        print(f"   ✅ Stream completed")
                        break
                    
                    elif event == 'stream_error':
                        print(f"   ❌ Stream error: {data['data']}")
                        break
                        
                except json.JSONDecodeError as e:
                    parse_errors += 1
                    print(f"   ⚠️ Parse error: {str(e)[:50]}...")
                except Exception as e:
                    print(f"   ❌ Processing error: {e}")
    
    # Results analysis
    print(f"\n   📊 Results Summary:")
    print(f"      Clean messages: {clean_messages}")
    print(f"      User echoes: {user_echoes} {'✅' if user_echoes == 0 else '❌'}")
    print(f"      JSON responses: {json_responses} {'✅' if json_responses == 0 else '❌'}")
    print(f"      Parse errors: {parse_errors} {'✅' if parse_errors == 0 else '❌'}")
    print(f"      Courses found: {'✅' if courses_found else '❌'}")
    
    # Overall assessment
    if courses_found and user_echoes == 0 and parse_errors == 0:
        print(f"   🎉 PERFECT: All issues fixed!")
    elif courses_found:
        print(f"   ⚠️ PARTIAL: Courses work but some issues remain")
    else:
        print(f"   ❌ ISSUES: Core functionality not working")

def is_user_message_echo(content, user_message):
    """Check if content is echoing the user message"""
    if not content or not user_message:
        return False
    
    content_lower = content.lower().strip()
    user_lower = user_message.lower().strip()
    
    if content_lower == user_lower:
        return True
    
    if len(user_lower) > 10 and user_lower in content_lower:
        similarity = len(user_lower) / len(content_lower)
        if similarity > 0.8:
            return True
    
    return False

def is_json_content(content):
    """Check if content is JSON"""
    if not content or not isinstance(content, str):
        return False
    
    trimmed = content.strip()
    if (trimmed.startswith('{') and trimmed.endswith('}')) or (trimmed.startswith('[') and trimmed.endswith(']')):
        try:
            parsed = json.loads(trimmed)
            if isinstance(parsed, dict) and ('courses' in parsed or 'success' in parsed):
                return True
        except json.JSONDecodeError:
            pass
    
    return False

if __name__ == "__main__":
    print("🧪 Comprehensive Test Suite for Chat Fixes")
    print("This will test JSON parsing, echo prevention, and course cards")
    print("Make sure the server is running: python main_with_agent.py\n")
    
    asyncio.run(test_all_fixes())