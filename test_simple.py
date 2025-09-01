#!/usr/bin/env python3
"""
Simple test script for the get_courses_info_html function
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the function directly from the course_server module
from course_server import get_courses_info_html

def test_function():
    """Test the get_courses_info_html function"""
    
    print("Testing get_courses_info_html function...")
    print("=" * 50)
    
    # Test 1: Valid Coursera search
    print("\nTest 1: Coursera search for 'python programming'")
    result1 = get_courses_info_html('coursera', ['python', 'programming'])
    
    if 'error' in result1:
        print(f"❌ Error: {result1['error']}")
    else:
        print(f"✅ Platform: {result1['platform']}")
        print(f"✅ Keywords: {result1['keywords']}")
        print(f"✅ Search URL: {result1['search_url']}")
        print(f"✅ HTML length: {len(result1['html_content'])} characters")
        print(f"✅ HTML preview: {result1['html_content'][:200]}...")
    
    print("\n" + "-" * 50)
    
    # Test 2: Valid Udemy search
    print("\nTest 2: Udemy search for 'machine learning'")
    result2 = get_courses_info_html('udemy', ['machine', 'learning'])
    
    if 'error' in result2:
        print(f"❌ Error: {result2['error']}")
    else:
        print(f"✅ Platform: {result2['platform']}")
        print(f"✅ Keywords: {result2['keywords']}")
        print(f"✅ Search URL: {result2['search_url']}")
        print(f"✅ HTML length: {len(result2['html_content'])} characters")
        print(f"✅ HTML preview: {result2['html_content'][:200]}...")
    
    print("\n" + "-" * 50)
    
    # Test 3: Invalid platform
    print("\nTest 3: Invalid platform 'invalid_platform'")
    result3 = get_courses_info_html('invalid_platform', ['test'])
    
    if 'error' in result3:
        print(f"✅ Expected error: {result3['error']}")
    else:
        print("❌ Should have returned an error")
    
    print("\n" + "-" * 50)
    
    # Test 4: Empty keywords
    print("\nTest 4: Empty keywords")
    result4 = get_courses_info_html('coursera', [])
    
    if 'error' in result4:
        print(f"✅ Expected error: {result4['error']}")
    else:
        print("❌ Should have returned an error")

if __name__ == '__main__':
    test_function()
