# server.py
from mcp.server.fastmcp import FastMCP
import requests
import os
import time
from datetime import datetime
from urllib.parse import quote_plus, urljoin
from bs4 import BeautifulSoup
import json

# Create an MCP server
mcp = FastMCP("Course")

# Rate limiting tracker
last_request_time = {}
MIN_REQUEST_INTERVAL = 5  # 5 seconds between requests to same domain

def get_domain(url):
    """Extract domain from URL for rate limiting"""
    from urllib.parse import urlparse
    return urlparse(url).netloc

def wait_for_rate_limit(url):
    """Wait if necessary to respect rate limits"""
    domain = get_domain(url)
    current_time = time.time()
    
    if domain in last_request_time:
        time_since_last = current_time - last_request_time[domain]
        if time_since_last < MIN_REQUEST_INTERVAL:
            wait_time = MIN_REQUEST_INTERVAL - time_since_last
            print(f"⏱️ Rate limiting: waiting {wait_time:.1f} seconds for {domain}")
            time.sleep(wait_time)
    
    last_request_time[domain] = time.time()

@mcp.tool()
async def search_courses(platform: str, keywords: list) -> dict:
    """Search for courses and return specific HTML elements for each platform
    
    Args:
        platform (str): The platform to search on. Must be one of: 'coursera', 'udemy', 'edx'
        keywords (list): List of keywords to search for (e.g. ['python', 'programming'] or ['AI', 'business'])
    
    Returns:
        dict: Dictionary containing the HTML content of relevant course elements
    
    Examples:
        search_courses('coursera', ['python', 'programming'])
        search_courses('udemy', ['data', 'science'])
        search_courses('edx', ['machine', 'learning'])
    """
    course_info_base_urls = {
        'coursera': 'https://www.coursera.org/search?query=',
        'udemy': 'https://www.udemy.com/courses/search/?q=',
        'edx': 'https://www.edx.org/search?q='
    }

    # Validate inputs
    if platform.lower() not in course_info_base_urls:
        return {
            'error': f'Platform "{platform}" not supported. Available platforms: {list(course_info_base_urls.keys())}',
            'course_elements': []
        }
    
    if not keywords:
        return {'error': 'Keywords cannot be empty', 'course_elements': []}
    
    # Build search URL
    query = ' '.join(keywords)
    search_url = course_info_base_urls[platform.lower()] + quote_plus(query)
    
    try:
        # Apply rate limiting and fetch
        wait_for_rate_limit(search_url)
        
        response = requests.get(search_url, timeout=10)
        response.raise_for_status()
        
        # Save full HTML for debugging
        os.makedirs('logs/full_html', exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_keywords = "_".join(k.replace(' ', '-') for k in keywords)
        html_filename = f'logs/full_html/{platform.lower()}_{safe_keywords}_{timestamp}.html'
        
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        # Parse HTML and extract platform-specific elements
        soup = BeautifulSoup(response.text, 'html.parser')
        course_elements = []
        
        if platform.lower() == 'coursera':
            # Get all elements with class "cds-ProductCard-gridCard"
            elements = soup.find_all('div', class_="cds-ProductCard-gridCard")
            for elem in elements:
                course_elements.append(str(elem))
                
        elif platform.lower() == 'udemy':
            # Get all elements with class "prefetching-wrapper-module--prefetching-wrapper--h55SO"
            elements = soup.find_all('div', class_="prefetching-wrapper-module--prefetching-wrapper--h55SO")
            for elem in elements:
                course_elements.append(str(elem))
                
        elif platform.lower() == 'edx':
            # Get all elements with title containing 'course'
            elements = soup.find_all(attrs={"title": lambda x: x and 'course' in x.lower()})
            for elem in elements:
                course_elements.append(str(elem))
        
        return {
            'platform': platform,
            'keywords': keywords,
            'search_url': search_url,
            'total_elements_found': len(course_elements),
            'course_elements': course_elements,
            'full_html_saved_to': html_filename,
            'note': f'Found {len(course_elements)} course elements for {platform}. Each element contains course information in HTML format.'
        }
        
    except requests.exceptions.Timeout:
        return {
            'error': 'Request timed out - the website took too long to respond',
            'platform': platform,
            'suggestion': 'Try again in a few minutes or use a different platform',
            'course_elements': []
        }
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            return {
                'error': 'Rate limit exceeded - too many requests to this platform',
                'platform': platform,
                'suggestion': 'Wait 60 seconds before trying this platform again, or try a different platform',
                'retry_after': '60 seconds',
                'course_elements': []
            }
        else:
            return {
                'error': f'HTTP error: {e.response.status_code} {e.response.reason}',
                'platform': platform,
                'course_elements': []
            }
    except Exception as e:
        return {
            'error': f'Failed to fetch courses: {str(e)}',
            'platform': platform,
            'suggestion': 'Check your internet connection or try a different platform',
            'course_elements': []
        }

@mcp.tool()
async def get_course_page(url: str) -> dict:
    """Get the full content of a specific course page
    
    Args:
        url (str): The course URL to fetch
    
    Returns:
        dict: Dictionary containing the course page HTML content (truncated to avoid token limits)
        
    Examples:
        get_course_page('https://www.coursera.org/learn/python-programming')
        get_course_page('https://www.udemy.com/course/complete-python-bootcamp/')
    """
    if not url or not url.startswith(('http://', 'https://')):
        return {'error': 'Invalid URL. Must start with http:// or https://'}
    
    try:
        wait_for_rate_limit(url)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Save full HTML for debugging
        os.makedirs('logs/course_pages', exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_url = url.replace('/', '_').replace(':', '_').replace('?', '_')[:50]
        html_filename = f'logs/course_pages/page_{safe_url}_{timestamp}.html'
        
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        # Truncate HTML content to avoid token limits (keep first 8KB)
        max_size = 8 * 1024  # 8KB
        truncated_html = response.text[:max_size]
        if len(response.text) > max_size:
            truncated_html += "\n\n<!-- CONTENT TRUNCATED TO AVOID TOKEN LIMITS -->"
        
        return {
            'url': url,
            'status_code': response.status_code,
            'html_content': truncated_html,
            'original_size': len(response.text),
            'truncated_size': len(truncated_html),
            'full_html_saved_to': html_filename,
            'note': f'Content truncated from {len(response.text)} to {len(truncated_html)} characters to avoid token limits'
        }
        
    except Exception as e:
        return {
            'error': f'Failed to fetch course page: {str(e)}',
            'url': url
        }

if __name__ == '__main__':
    mcp.run()
