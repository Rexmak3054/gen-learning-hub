#!/usr/bin/env python3
"""
Standalone test for both functions
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

def fetch_page_content(url: str, platform: str = None) -> dict:
    """Fetch detailed content from a specific course page or any URL for deeper analysis
    
    Args:
        url: The URL to fetch content from (can be a course detail page, instructor page, etc.)
        platform: Optional platform name for context (coursera, udemy, edx)
    
    Returns:
        Dictionary containing the URL and HTML content of the requested page
    """
    if not url:
        return {'error': 'URL cannot be empty'}
    
    # Basic URL validation
    if not url.startswith(('http://', 'https://')):
        return {'error': 'URL must start with http:// or https://'}
    
    try:
        # Set headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Make request to get HTML page
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        return {
            'url': url,
            'platform': platform,
            'status_code': response.status_code,
            'content_type': response.headers.get('content-type', 'unknown'),
            'html_content': response.text,
            'content_length': len(response.text)
        }
        
    except requests.exceptions.Timeout:
        return {
            'error': 'Request timed out',
            'url': url,
            'platform': platform
        }
    except requests.exceptions.HTTPError as e:
        return {
            'error': f'HTTP error: {e.response.status_code} {e.response.reason}',
            'url': url,
            'platform': platform
        }
    except Exception as e:
        return {
            'error': f'Failed to fetch page: {str(e)}',
            'url': url,
            'platform': platform
        }

# Test both functions
if __name__ == '__main__':
    print("Testing both course research functions...")
    print("=" * 60)
    
    # Test 1: Search for courses
    print("\nStep 1: Search for Python courses on Coursera")
    search_result = get_courses_info_html('udemy', ['python'])
    
    if 'error' in search_result:
        print(f"❌ Search failed: {search_result['error']}")
    else:
        print(f"✅ Search successful!")
        print(f"   Search URL: {search_result['search_url']}")
        print(f"   HTML length: {len(search_result['html_content'])} characters")
        
        # Test 2: Fetch a specific course page
        print("\nStep 2: Testing fetch_page_content with a course URL")
        # Use a known Coursera course URL for testing
        test_course_url = "https://www.coursera.org/learn/python"
        
        page_result = fetch_page_content(test_course_url, 'coursera')
        
        if 'error' in page_result:
            print(f"❌ Page fetch failed: {page_result['error']}")
        else:
            print(f"✅ Page fetch successful!")
            print(f"   URL: {page_result['url']}")
            print(f"   Status: {page_result['status_code']}")
            print(f"   Content Type: {page_result['content_type']}")
            print(f"   HTML length: {page_result['content_length']} characters")
            print(f"   HTML preview: {page_result['html_content'][:150]}...")
    
    print("\n" + "=" * 60)
    print("Test completed!")
