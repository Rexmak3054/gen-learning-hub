#!/usr/bin/env python3
"""
Quick test script for the FastAPI backend
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_health():
    """Test the health endpoint"""
    print("🏥 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed!")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Is it running?")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_course_search():
    """Test the course search endpoint"""
    print("\n🔍 Testing course search endpoint...")
    try:
        data = {
            "query": "python programming",
            "k": 5
        }
        response = requests.post(
            f"{BASE_URL}/api/search-courses",
            headers={"Content-Type": "application/json"},
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Course search successful!")
            print(f"   Found {result.get('total_results', 0)} courses")
            if result.get('courses'):
                print(f"   First course: {result['courses'][0].get('title', 'N/A')}")
            return True
        else:
            print(f"❌ Course search failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Course search error: {e}")
        return False

def test_research_agent_health():
    """Test the research agent health endpoint"""
    print("\n🤖 Testing research agent health...")
    try:
        response = requests.get(f"{BASE_URL}/api/courses/health")
        if response.status_code == 200:
            result = response.json()
            print("✅ Research agent health check passed!")
            print(f"   Agent initialized: {result.get('research_agent_initialized', False)}")
            print(f"   Tools loaded: {result.get('tools_loaded', 0)}")
            return True
        else:
            print(f"❌ Research agent health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Research agent health check error: {e}")
        return False

def test_debug_tools():
    """Test the debug tools endpoint"""
    print("\n🔧 Testing debug tools endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/debug/tools")
        if response.status_code == 200:
            result = response.json()
            print("✅ Debug tools check passed!")
            print(f"   Total tools: {result.get('total_tools', 0)}")
            
            if result.get('tools'):
                print("   Available tools:")
                for tool in result['tools'][:3]:  # Show first 3 tools
                    print(f"     - {tool.get('name', 'N/A')}: {tool.get('description', 'N/A')[:50]}...")
            return True
        else:
            print(f"❌ Debug tools check failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Debug tools error: {e}")
        return False

def test_agent_search_direct():
    """Test the new agent search endpoint"""
    print("\n🔍 Testing agent search direct endpoint...")
    try:
        data = {
            "query": "machine learning basics",
            "k": 3
        }
        response = requests.post(
            f"{BASE_URL}/api/agent-search-courses",
            headers={"Content-Type": "application/json"},
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Agent search direct successful!")
            print(f"   Success: {result.get('success', False)}")
            print(f"   Total courses: {result.get('total_results', 0)}")
            
            if result.get('courses'):
                print(f"   First course: {result['courses'][0].get('title', 'N/A')[:50]}...")
                
            return True
        else:
            print(f"❌ Agent search direct failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Agent search direct error: {e}")
        return False

def test_api_docs():
    """Test that API documentation is accessible"""
    print("\n📖 Testing API documentation...")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ API documentation is accessible!")
            print(f"   Visit: {BASE_URL}/docs")
            return True
        else:
            print(f"❌ API documentation failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API documentation error: {e}")
        return False

def main():
    print("🧪 FastAPI Backend Test Suite")
    print("=" * 40)
    
    tests = [
        test_health,
        test_api_docs,
        test_research_agent_health,
        test_debug_tools,
        test_course_search,
        test_agent_search_direct,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your FastAPI backend is working correctly.")
        print(f"🌐 API Documentation: {BASE_URL}/docs")
        print(f"🔍 Alternative Docs: {BASE_URL}/redoc")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        print("💡 Make sure:")
        print("   - The server is running (./start.sh)")
        print("   - Your .env file is configured")
        print("   - OpenAI API key is set")
        print("   - course_server.py is accessible")
        
        sys.exit(1)

if __name__ == "__main__":
    main()
