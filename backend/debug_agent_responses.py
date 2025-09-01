#!/usr/bin/env python3
"""
Debug what the agent is actually generating
"""

import asyncio
import aiohttp
import json

async def debug_agent_responses():
    """Debug what responses the agent is generating"""
    
    base_url = "http://localhost:8001"
    
    print("🔍 Debug Agent Response Generation")
    print("=" * 50)
    
    try:
        async with aiohttp.ClientSession() as session:
            # Start session
            async with session.post(f"{base_url}/api/chat/start") as resp:
                data = await resp.json()
                session_id = data["session_id"]
                print(f"✅ Session: {session_id}")
            
            print(f"\n📨 Sending: 'Hello!'")
            print("Raw agent responses:")
            print("-" * 30)
            
            async with session.post(
                f"{base_url}/api/chat/stream",
                json={"session_id": session_id, "message": "Hello!"}
            ) as resp:
                
                async for line in resp.content:
                    line_str = line.decode('utf-8').strip()
                    
                    if line_str.startswith('data: ') and len(line_str) > 6:
                        try:
                            data = json.loads(line_str[6:])
                            event = data.get('event')
                            
                            if event == 'message_added' and data['data']['message_type'] == 'assistant':
                                content = data['data']['content']
                                print(f"Response: {repr(content)}")
                                
                                # Analyze why it might be filtered
                                print(f"  Length: {len(content)}")
                                print(f"  Starts with {{: {content.strip().startswith('{')}")
                                print(f"  Contains 'courses': {'courses' in content.lower()}")
                                print(f"  Contains 'success': {'success' in content.lower()}")
                                print(f"  Contains 'helpful ai': {'helpful ai' in content.lower()}")
                                print(f"  Contains 'process': {'process' in content.lower()}")
                                print()
                                
                        except json.JSONDecodeError as e:
                            print(f"Parse error: {e}")
            
            # Test with course request
            print(f"\n📨 Sending: 'I want to learn Python'")
            print("Raw agent responses:")
            print("-" * 30)
            
            async with session.post(
                f"{base_url}/api/chat/stream",
                json={"session_id": session_id, "message": "I want to learn Python"}
            ) as resp:
                
                response_count = 0
                async for line in resp.content:
                    line_str = line.decode('utf-8').strip()
                    
                    if line_str.startswith('data: ') and len(line_str) > 6:
                        try:
                            data = json.loads(line_str[6:])
                            event = data.get('event')
                            
                            if event == 'message_added' and data['data']['message_type'] == 'assistant':
                                response_count += 1
                                content = data['data']['content']
                                print(f"Response {response_count}: {repr(content[:100])}")
                                
                                # Detailed analysis
                                is_json = content.strip().startswith('{')
                                is_tool_result = '"courses"' in content or '"success"' in content
                                is_system = 'helpful ai' in content.lower() or 'process' in content.lower()
                                
                                print(f"  Analysis:")
                                print(f"    JSON format: {is_json}")
                                print(f"    Tool result: {is_tool_result}")
                                print(f"    System message: {is_system}")
                                print(f"    Should filter: {is_json or is_tool_result or is_system}")
                                print()
                                
                        except json.JSONDecodeError as e:
                            print(f"Parse error: {e}")
            
    except Exception as e:
        print(f"❌ Debug failed: {e}")

if __name__ == "__main__":
    print("🔍 This will show exactly what the agent is generating")
    print("and why responses might be getting filtered out.")
    print()
    print("Make sure clean agent is running: python clean_agent_chat.py")
    print()
    
    asyncio.run(debug_agent_responses())
