#!/usr/bin/env python3
"""
Simple debug script to test server connectivity
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def debug_connection():
    """Debug the server connection step by step"""
    
    print("🔧 Grace Papers Backend - Connection Debug")
    print("=" * 50)
    
    # Test 1: Basic server health
    print("\n1️⃣ Testing basic server connectivity...")
    try:
        response = requests.get(f"{BASE_URL}/test", timeout=5)
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.json()}")
        if response.status_code == 200:
            print("✅ Server is running and responding!")
        else:
            print("❌ Server responded but with error status")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection refused - is the server running?")
        print("   Start server with: python main_with_agent.py")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    # Test 2: Health endpoint
    print("\n2️⃣ Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        result = response.json()
        print(f"   Health Status: {result['status']}")
        print(f"   Message: {result['message']}")
        print(f"   Version: {result['version']}")
        print("✅ Health check passed!")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test 3: Chat start endpoint
    print("\n3️⃣ Testing chat start endpoint...")
    try:
        start_data = {"user_id": "debug-test"}
        response = requests.post(f"{BASE_URL}/api/chat/start", json=start_data)
        result = response.json()
        
        if result["success"]:
            session_id = result["session_id"]
            print(f"✅ Chat session created: {session_id[:12]}...")
            return session_id
        else:
            print(f"❌ Chat start failed: {result.get('error')}")
            return False
    except Exception as e:
        print(f"❌ Chat start error: {e}")
        return False

def debug_streaming(session_id):
    """Debug the streaming functionality"""
    print("\n4️⃣ Testing streaming endpoint...")
    
    try:
        stream_data = {
            "session_id": session_id,
            "message": "Hello, test message"
        }
        
        print("   Sending streaming request...")
        response = requests.post(
            f"{BASE_URL}/api/chat/stream",
            json=stream_data,
            stream=True,
            timeout=10
        )
        
        print(f"   Stream response status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type')}")
        
        if response.status_code == 200:
            print("   📡 Reading stream data...")
            line_count = 0
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    line_count += 1
                    print(f"   Line {line_count}: {line_str[:100]}...")
                    
                    if line_count >= 5:  # Limit output for debugging
                        print("   ... (stopping after 5 lines)")
                        break
            
            print("✅ Streaming test completed!")
            return True
        else:
            print(f"❌ Streaming failed with status {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Streaming test error: {e}")
        return False

def main():
    """Run all debug tests"""
    print("Starting Grace Papers Backend Debug...")
    
    # Test basic connectivity
    session_id = debug_connection()
    
    if session_id:
        # Test streaming
        debug_streaming(session_id)
        
        print("\n" + "=" * 50)
        print("🎉 Debug Complete!")
        print("\nIf all tests passed, the server is working correctly.")
        print("If there were errors, check:")
        print("  • Server is running: python main_with_agent.py")
        print("  • No other process is using port 8000")
        print("  • Firewall isn't blocking the connection")
    else:
        print("\n❌ Server connectivity failed!")
        print("Make sure to start the server first:")
        print("  cd /Users/hiufungmak/grace-papers-gen/backend")
        print("  python main_with_agent.py")

if __name__ == "__main__":
    main()
