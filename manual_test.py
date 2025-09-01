#!/usr/bin/env python3
"""
Manual test script - run this locally to test the function
"""

# Test the function logic without making actual HTTP requests
def test_function_logic():
    """Test the function logic and URL construction"""
    from urllib.parse import quote_plus
    
    def simulate_get_courses_info_html(platform: str, keywords: list) -> dict:
        """Simulate the function logic without HTTP requests"""
        course_info_base_urls = {
            'coursera': 'https://www.coursera.org/search?query=',
            'udemy': 'https://www.udemy.com/courses/search/?q=',
            'edx': 'https://www.edx.org/search?q='
        }

        # Parse the keywords to the corresponding platform url
        if platform.lower() not in course_info_base_urls:
            return {'error': f'Platform "{platform}" not supported. Available platforms: {list(course_info_base_urls.keys())}'}
        
        if not keywords:
            return {'error': 'Keywords cannot be empty'}
        
        # Join keywords for search query
        query = ' '.join(keywords)
        search_url = course_info_base_urls[platform.lower()] + quote_plus(query)
        
        return {
            'platform': platform,
            'keywords': keywords,
            'search_url': search_url,
            'status': 'URL constructed successfully (no HTTP request made)'
        }
    
    print("Testing function logic...")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        ('coursera', ['python', 'programming']),
        ('udemy', ['machine learning']),
        ('edx', ['data science']),
        ('invalid_platform', ['test']),  # Should error
        ('coursera', []),  # Should error
    ]
    
    for i, (platform, keywords) in enumerate(test_cases, 1):
        print(f"\nTest {i}: platform='{platform}', keywords={keywords}")
        result = simulate_get_courses_info_html(platform, keywords)
        
        if 'error' in result:
            print(f"❌ Error (expected): {result['error']}")
        else:
            print(f"✅ Success!")
            print(f"   Platform: {result['platform']}")
            print(f"   Keywords: {result['keywords']}")
            print(f"   Search URL: {result['search_url']}")
        print("-" * 30)

if __name__ == '__main__':
    test_function_logic()
    
    print("\n" + "=" * 50)
    print("MANUAL TESTING INSTRUCTIONS:")
    print("=" * 50)
    print("1. Run this command to test the actual function:")
    print("   python3 -c \"from course_server import get_courses_info_html; result = get_courses_info_html('coursera', ['python']); print('Success!' if 'html_content' in result else f'Error: {result}')\"")
    print("\n2. Or run the MCP server:")
    print("   python3 course_server.py")
    print("\n3. Test URLs in browser:")
    print("   https://www.coursera.org/search?query=python%20programming")
    print("   https://www.udemy.com/courses/search/?q=machine%20learning")
    print("   https://www.edx.org/search?q=data%20science")
