#!/usr/bin/env python3
"""
Test the clean agent step by step
"""

import asyncio
import aiohttp
import json

async def test_clean_step_by_step():
    """Test the clean agent step by step"""
    
    base_url = "http://localhost:8001"
    
    print("🧪 Clean Agent Step-by-Step Test")
    print("=" * 40)
    
    try:
        async with aiohttp.ClientSession() as session:
            # 1. Health check
            print("1. Health Check...")
            async with session.get(f"{base_url}/health") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"   ✅ Status: {data['status']}")
                    print(f"   Agent: {data['agent_initialized']}")
                    print(f"   Tools: {data['tools_loaded']}")
                    
                    if not data['agent_initialized']:
                        print("   ❌ Agent not ready - stopping test")
                        return
                else:
                    print(f"   ❌ Health failed: {resp.status}")
                    return
            
            # 2. Start session
            print("\\n2. Starting Session...")
            async with session.post(f"{base_url}/api/chat/start") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    session_id = data["session_id"]
                    print(f"   ✅ Session: {session_id}")
                else:
                    print(f"   ❌ Session failed: {resp.status}")
                    return
            
            # 3. Test simple message
            print("\\n3. Testing Simple Message...")
            await test_single_message(session, base_url, session_id, "Hello!", "general")
            
            # 4. Test course request
            print("\\n4. Testing Course Request...")
            await test_single_message(session, base_url, session_id, "I want to learn Python programming", "course")
            
            print("\\n🎉 Step-by-step test completed!")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

async def test_single_message(session, base_url, session_id, message, test_type):
    """Test a single message"""
    
    print(f"   Sending: '{message}'")
    
    events_received = []
    parse_errors = 0
    
    try:
        async with session.post(
            f"{base_url}/api/chat/stream",
            json={"session_id": session_id, "message": message}
        ) as resp:
            
            if resp.status != 200:
                print(f"   ❌ HTTP {resp.status}")
                return
            
            async for line in resp.content:
                line_str = line.decode('utf-8').strip()
                
                if line_str.startswith('data: ') and len(line_str) > 6:
                    json_str = line_str[6:].strip()
                    if not json_str:
                        continue
                    
                    try:
                        data = json.loads(json_str)
                        event = data.get('event', 'unknown')
                        events_received.append(event)
                        
                        if event == 'message_added':
                            msg_type = data['data']['message_type']
                            content = data['data']['content']
                            print(f"   📝 {msg_type}: {content[:60]}...")
                        
                        elif event == 'courses_ready':
                            course_count = len(data['data'].get('course_uuids', []))
                            print(f"   📚 Courses: {course_count} UUIDs ready")
                        
                        elif event == 'stream_complete':
                            print(f"   ✅ Complete")
                            break
                        
                        elif event == 'stream_error':
                            print(f"   ❌ Error: {data['data']}")
                            break
                            
                    except json.JSONDecodeError as e:
                        parse_errors += 1
                        print(f"   ⚠️ Parse error {parse_errors}: {e}")
                        print(f"   Raw: {repr(json_str[:100])}")
    
    except Exception as e:
        print(f"   ❌ Stream error: {e}")
    
    # Summary
    print(f"   📊 Events: {events_received}")
    if parse_errors > 0:
        print(f"   ⚠️ Parse errors: {parse_errors}")
    
    if test_type == "course" and "courses_ready" not in events_received:
        print(f"   ⚠️ Expected course tool call but none detected")
    elif test_type == "general" and "courses_ready" in events_received:
        print(f"   ⚠️ Unexpected course tool call for general message")

if __name__ == "__main__":
    print("🔍 This test checks the clean agent implementation step by step")
    print("Make sure the server is running: python clean_agent_chat.py")
    print()
    
    asyncio.run(test_clean_step_by_step())
