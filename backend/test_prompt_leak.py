#!/usr/bin/env python3
"""
Test to verify system prompt leakage is fixed
"""

import asyncio
import aiohttp
import json

async def test_system_prompt_fix():
    """Test that system prompts don't leak into chat responses"""
    
    base_url = "http://localhost:8000"
    
    print("🔍 Testing System Prompt Leakage Fix...")
    print("=" * 50)
    
    try:
        async with aiohttp.ClientSession() as session:
            # Start a chat session
            print("1. Starting chat session...")
            async with session.post(
                f"{base_url}/api/chat/start",
                json={"user_id": "prompt-leak-test"}
            ) as resp:
                data = await resp.json()
                session_id = data["session_id"]
                print(f"   ✅ Session: {session_id}")
            
            # Test messages that previously caused system prompt leaks
            test_cases = [
                ("hello", "Should get friendly greeting"),
                ("what can you do for me", "Should explain capabilities naturally"),
                ("I want to learn Python", "Should offer to find courses"),
                ("tell me about yourself", "Should be conversational")
            ]
            
            for i, (message, expectation) in enumerate(test_cases, 1):
                print(f"\n{i}. Testing: \"{message}\"")
                print(f"   Expected: {expectation}")
                
                system_prompt_detected = False
                clean_responses = []
                
                async with session.post(
                    f"{base_url}/api/chat/stream",
                    json={"session_id": session_id, "message": message}
                ) as resp:
                    
                    async for line in resp.content:
                        line_str = line.decode('utf-8').strip()
                        
                        if line_str.startswith('data: ') and len(line_str) > 6:
                            try:
                                json_str = line_str[6:].strip()
                                if not json_str:
                                    continue
                                    
                                data = json.loads(json_str)
                                
                                if data.get('event') == 'message_added':
                                    content = data['data']['content']
                                    msg_type = data['data']['message_type']
                                    
                                    if msg_type == 'agent_response':\n                                        # Check for system prompt leakage\n                                        leak_indicators = [\n                                            \"this is a continuation of an ongoing conversation\",\n                                            \"user's current message:\",\n                                            \"respond naturally and helpfully\",\n                                            \"previous conversation context:\"\n                                        ]\n                                        \n                                        if any(indicator in content.lower() for indicator in leak_indicators):\n                                            system_prompt_detected = True\n                                            print(f\"   ❌ SYSTEM PROMPT LEAK: {content[:60]}...\")\n                                        else:\n                                            clean_responses.append(content)\n                                            print(f\"   ✅ Clean response: {content[:60]}...\")\n                                \n                                elif data.get('event') == 'stream_complete':\n                                    break\n                                    \n                            except json.JSONDecodeError:\n                                continue\n                \n                # Results for this test case\n                if system_prompt_detected:\n                    print(f\"   🚨 FAILED: System prompt leaked\")\n                elif clean_responses:\n                    print(f\"   🎉 SUCCESS: {len(clean_responses)} clean responses\")\n                else:\n                    print(f\"   ⚠️ WARNING: No responses received\")\n                \n                # Small delay between tests\n                await asyncio.sleep(0.5)\n            \n            print(f\"\\n📊 System Prompt Leak Test Summary:\")\n            print(f\"   All tests should show clean responses with no system prompt leakage.\")\n            \n    except Exception as e:\n        print(f\"❌ Test failed: {e}\")\n        import traceback\n        traceback.print_exc()\n\nif __name__ == \"__main__\":\n    print(\"🧪 System Prompt Leakage Test\")\n    print(\"This verifies that internal system prompts don't appear in chat responses.\")\n    print(\"Make sure the server is running: python main_with_agent.py\\n\")\n    \n    asyncio.run(test_system_prompt_fix())