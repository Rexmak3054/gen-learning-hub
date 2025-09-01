#!/usr/bin/env python3
"""
Quick fix test - Run this after starting the server to test the specific issue
"""

import asyncio
import aiohttp
import json

async def test_business_analyst_query():
    """Test the specific business analyst query that was failing"""
    
    base_url = "http://localhost:8000"
    
    print("🔧 Testing Business Analyst Query Fix...")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Start a chat session
            print("1. Starting chat session...")
            async with session.post(
                f"{base_url}/api/chat/start",
                json={"user_id": "fix-test"}
            ) as resp:
                data = await resp.json()
                session_id = data["session_id"]
                print(f"   ✅ Session: {session_id}")
            
            # Test the problematic query
            print("2. Testing business analyst query...")
            test_message = "I am a business analyst, i want to learn about how to use AI to create business report"
            
            message_count = 0
            courses_found = False
            json_responses = 0
            
            async with session.post(
                f"{base_url}/api/chat/stream",
                json={
                    "session_id": session_id,
                    "message": test_message
                }
            ) as resp:
                
                async for line in resp.content:
                    line_str = line.decode('utf-8').strip()
                    if line_str.startswith('data: ') and len(line_str) > 6:
                        try:
                            json_str = line_str[6:]\n                            if not json_str.strip():\n                                continue\n                                \n                            data = json.loads(json_str)\n                            event = data.get('event')\n                            \n                            if event == 'message_added':\n                                content = data['data']['content']\n                                msg_type = data['data']['message_type']\n                                \n                                # Check if this is a JSON response\n                                is_json = content.strip().startswith('{') and content.strip().endswith('}')\n                                if is_json:\n                                    json_responses += 1\n                                    print(f\"   ⚠️ Found JSON response (will be filtered): {len(content)} chars\")\n                                else:\n                                    message_count += 1\n                                    print(f\"   💬 Clean message ({msg_type}): {content[:60]}...\")\n                            \n                            elif event == 'courses_ready':\n                                courses_found = True\n                                course_count = len(data['data']['courses'])\n                                query = data['data']['query']\n                                print(f\"   🎯 COURSES READY: {course_count} courses for '{query[:30]}...'\")\n                                print(f\"   📝 Course sample: {data['data']['courses'][0]['title'] if data['data']['courses'] else 'None'}\")\n                            \n                            elif event == 'stream_complete':\n                                print(\"   ✅ Stream completed\")\n                                break\n                            \n                            elif event == 'stream_error':\n                                print(f\"   ❌ Stream error: {data['data']}\")\n                                break\n                                \n                        except json.JSONDecodeError as e:\n                            print(f\"   ⚠️ JSON decode error for line: {line_str[:50]}...\")\n                            print(f\"   Error: {e}\")\n            \n            print(f\"\\n📊 Fix Test Results:\")\n            print(f\"   Clean messages: {message_count}\")\n            print(f\"   JSON responses filtered: {json_responses}\")\n            print(f\"   Courses found: {'✅ Yes' if courses_found else '❌ No'}\")\n            \n            if courses_found and json_responses == 0:\n                print(\"\\n🎉 SUCCESS: Fix is working properly!\")\n            elif courses_found:\n                print(\"\\n⚠️ PARTIAL: Courses found but JSON filtering needed\")\n            else:\n                print(\"\\n❌ ISSUE: No courses found in stream\")\n            \n    except Exception as e:\n        print(f\"❌ Test failed: {e}\")\n        import traceback\n        traceback.print_exc()\n\nif __name__ == \"__main__\":\n    print(\"Testing the specific issue with JSON responses and course cards...\")\n    print(\"Make sure the server is running with: python main_with_agent.py\")\n    print()\n    \n    asyncio.run(test_business_analyst_query())