#!/usr/bin/env python3
"""
Quick test to see what the agent is actually returning
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_agent_debug():
    """Test the agent with debug logging"""
    print("🔍 Testing agent search with debug logging...")
    
    try:
        data = {
            "query": "python programming",
            "k": 3
        }
        
        response = requests.post(
            f"{BASE_URL}/api/agent-search-courses",
            headers={"Content-Type": "application/json"},
            json=data
        )
        
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        # Check if tools are loaded
        tools_response = requests.get(f"{BASE_URL}/api/debug/tools")
        tools_result = tools_response.json()
        print(f"\nTools loaded: {tools_result.get('total_tools', 0)}")
        
        if tools_result.get('tools'):
            print("Available tools:")
            for tool in tools_result['tools']:
                print(f"  - {tool.get('name')}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_agent_debug()
