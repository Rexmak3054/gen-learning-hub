#!/usr/bin/env python3
"""
Debug the SSE parsing issue
"""

import asyncio
import aiohttp
import json

async def debug_sse_stream():
    """Debug the SSE stream parsing"""
    
    base_url = "http://localhost:8001"
    
    print("🔍 Debugging SSE Stream...")
    print("=" * 40)
    
    try:
        async with aiohttp.ClientSession() as session:
            # Start session
            async with session.post(f"{base_url}/api/chat/start") as resp:
                data = await resp.json()
                session_id = data["session_id"]
                print(f"Session: {session_id}")
            
            # Send a simple message and debug the raw stream
            print(f"\\nSending message: 'Hello!'")
            print("Raw SSE stream:")
            print("-" * 30)
            
            async with session.post(
                f"{base_url}/api/chat/stream",
                json={"session_id": session_id, "message": "Hello!"}
            ) as resp:
                
                line_count = 0
                async for line in resp.content:
                    line_str = line.decode('utf-8')
                    line_count += 1
                    
                    print(f"Line {line_count}: {repr(line_str)}")
                    
                    if line_str.startswith('data: '):
                        json_part = line_str[6:].strip()
                        print(f"  JSON part: {repr(json_part)}")
                        
                        if json_part:
                            try:
                                # Try to parse the JSON
                                data = json.loads(json_part)
                                print(f"  ✅ Parsed: {data.get('event', 'unknown')} event")
                            except json.JSONDecodeError as e:
                                print(f"  ❌ JSON Error: {e}")
                                print(f"  ❌ Error at char {e.pos}: {repr(json_part[max(0, e.pos-10):e.pos+10])}")
                                
                                # Try to find where the JSON might be split
                                if '{' in json_part and '}' in json_part:
                                    # Find first complete JSON object
                                    brace_count = 0
                                    first_json_end = -1
                                    for i, char in enumerate(json_part):
                                        if char == '{':
                                            brace_count += 1
                                        elif char == '}':
                                            brace_count -= 1
                                            if brace_count == 0:
                                                first_json_end = i
                                                break
                                    
                                    if first_json_end > 0:
                                        first_json = json_part[:first_json_end + 1]
                                        rest = json_part[first_json_end + 1:]
                                        print(f"  🔍 First JSON: {repr(first_json)}")
                                        print(f"  🔍 Remaining: {repr(rest)}")
                                        
                                        try:
                                            parsed_first = json.loads(first_json)
                                            print(f"  ✅ First JSON parsed: {parsed_first.get('event', 'unknown')}")
                                        except Exception as e2:
                                            print(f"  ❌ Still can't parse first JSON: {e2}")
                    
                    # Stop after reasonable number of lines for debugging
                    if line_count > 20:
                        print("... (truncated for debugging)")
                        break
            
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔍 SSE Stream Debug Tool")
    print("This will show the raw SSE stream to identify parsing issues.")
    print("Make sure the clean agent is running:")
    print("cd backend && python clean_agent_chat.py")
    print()
    
    asyncio.run(debug_sse_stream())