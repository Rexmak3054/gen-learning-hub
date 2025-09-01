#!/usr/bin/env python3
"""
Quick test for clean agent startup
"""

import subprocess
import time
import requests
import json

def test_clean_agent_startup():
    """Test if the clean agent starts properly"""
    
    print("🧪 Testing Clean Agent Startup...")
    print("=" * 40)
    
    try:
        # Test health endpoint
        print("1. Testing health endpoint...")
        response = requests.get("http://localhost:8001/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {data['status']}")
            print(f"   Agent initialized: {data['agent_initialized']}")
            print(f"   Tools loaded: {data['tools_loaded']}")
            
            if not data['agent_initialized']:
                print("   ⚠️ Agent not initialized - check logs for errors")
                return False
            
            if data['tools_loaded'] == 0:
                print("   ⚠️ No tools loaded - check MCP server connection")
                return False
                
            print("   🎉 Clean agent is running properly!")
            return True
            
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to clean agent on port 8001")
        print("   💡 Start with: python clean_agent_chat.py")
        return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False

def test_simple_message():
    """Test sending a simple message"""
    
    print("\\n2. Testing simple message...")
    
    try:
        # Start session
        start_response = requests.post("http://localhost:8001/api/chat/start")
        if start_response.status_code != 200:
            print(f"   ❌ Failed to start session: {start_response.status_code}")
            return
        
        session_data = start_response.json()
        session_id = session_data["session_id"]
        print(f"   ✅ Session created: {session_id}")
        
        # Send message and get raw response
        stream_response = requests.post(
            "http://localhost:8001/api/chat/stream",
            json={"session_id": session_id, "message": "Hello!"},
            stream=True,
            timeout=10
        )
        
        if stream_response.status_code != 200:
            print(f"   ❌ Stream failed: {stream_response.status_code}")
            return
        
        print("   📡 Raw SSE stream:")
        line_count = 0
        
        for line in stream_response.iter_lines(decode_unicode=True):
            line_count += 1
            if line_count > 10:  # Limit output for debugging
                print("   ... (truncated)")
                break
                
            if line.startswith('data: '):
                json_part = line[6:].strip()
                print(f"   Line {line_count}: {repr(json_part[:100])}...")
                
                if json_part:
                    try:
                        data = json.loads(json_part)
                        print(f"      ✅ Event: {data.get('event', 'unknown')}")
                    except json.JSONDecodeError as e:
                        print(f"      ❌ JSON Error at char {e.pos}: {e}")
                        
        print("   📊 Stream test completed")
        
    except Exception as e:
        print(f"   ❌ Message test error: {e}")

if __name__ == "__main__":
    print("🔍 Clean Agent Quick Test")
    print("This tests basic functionality and SSE parsing.")
    print()
    
    # Test startup
    if test_clean_agent_startup():
        # Test messaging
        test_simple_message()
    
    print("\\n💡 If issues persist, check the server logs for more details.")