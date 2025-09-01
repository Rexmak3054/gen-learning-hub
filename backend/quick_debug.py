#!/usr/bin/env python3
"""
Quick test to see what's wrong
"""

import requests
import json

def quick_test():
    """Quick test to see the issue"""
    
    print("🔍 Quick Debug Test")
    print("=" * 30)
    
    try:
        # Start session
        start_resp = requests.post("http://localhost:8001/api/chat/start")
        session_id = start_resp.json()["session_id"]
        print(f"Session: {session_id}")
        
        # Send simple message
        print(f"\\nSending: 'Hello!'")
        
        stream_resp = requests.post(
            "http://localhost:8001/api/chat/stream",
            json={"session_id": session_id, "message": "Hello!"},
            stream=True
        )
        
        responses = []
        for line in stream_resp.iter_lines(decode_unicode=True):
            if line.startswith('data: '):
                try:
                    data = json.loads(line[6:])
                    if data.get('event') == 'message_added' and data['data']['message_type'] == 'assistant':
                        content = data['data']['content']
                        responses.append(content)
                        print(f"Response: {content}")
                except:
                    pass
        
        print(f"\\nTotal responses: {len(responses)}")
        
        if len(responses) == 1 and "I understand your question" in responses[0]:
            print("❌ PROBLEM: Getting fallback response instead of natural response")
            print("💡 This means all agent responses are being filtered out")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    quick_test()
