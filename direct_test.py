#!/usr/bin/env python3
"""
Direct test of the function
"""
import requests
from urllib.parse import quote_plus

def get_courses_info_html(platform: str, keywords: list) -> dict:
    """Returns the brief information of the course information from the selected platform according to the keyword search"""
    course_info_base_urls = {
        'coursera': 'https://www.coursera.org/search?query=',
        'udemy': 'https://www.udemy.com/courses/search/?q=',
        'edx': 'https://www.edx.org/search?q='
    }

    # Parse the keywords to the corresponding platform url and request the information
    if platform.lower() not in course_info_base_urls:
        return {'error': f'Platform "{platform}" not supported. Available platforms: {list(course_info_base_urls.keys())}'}
    
    if not keywords:
        return {'error': 'Keywords cannot be empty'}
    
    # Join keywords for search query
    query = ' '.join(keywords)
    search_url = course_info_base_urls[platform.lower()] + quote_plus(query)
    
    try:
        # Make request to get HTML page
        response = requests.get(search_url, timeout=10)
        response.raise_for_status()
        
        return {
            'platform': platform,
            'keywords': keywords,
            'search_url': search_url,
            'html_content': response.text
        }
        
    except Exception as e:
        return {
            'error': f'Failed to fetch HTML: {str(e)}',
            'platform': platform,
            'search_url': search_url
        }

# Test the function
if __name__ == '__main__':
    print("Testing get_courses_info_html function...")
    
    # Test 1: Valid Coursera search
    print("\nTest 1: Coursera search")
    result = get_courses_info_html('coursera', ['python'])
    
    if 'error' in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Success! URL: {result['search_url']}")
        print(f"HTML length: {len(result['html_content'])} characters")
        print(f"HTML starts with: {result['html_content'][:100]}...")
    
    # Test 2: Error case
    print("\nTest 2: Invalid platform")
    result2 = get_courses_info_html('invalid', ['test'])
    print(f"Expected error: {result2.get('error', 'No error returned')}")
