# server.py
from mcp.server.fastmcp import FastMCP
import requests
import os
import time
from datetime import datetime
from urllib.parse import quote_plus, urljoin
from bs4 import BeautifulSoup
import json
from edx_scraper import EdxScraper
from coursera_scraper import CourseraScraper
from udemy_scraper import UdemyScraper
from course_info_handler import CourseStore

# Add imports for vector search
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
from dotenv import load_dotenv
load_dotenv()


import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_tools.log'),
        logging.StreamHandler()  # Also print to console
    ]
)
logger = logging.getLogger(__name__)

# Create an MCP server
mcp = FastMCP("Course")

# Initialize OpenSearch and other clients for vector search
REGION = os.getenv("AWS_REGION", "ap-southeast-2")
SERVICE = "aoss"  # Serverless
OS_ENDPOINT = os.environ["OS_ENDPOINT"]
HOST = OS_ENDPOINT.replace("https://", "")
INDEX = "courses-v1"

auth = AWSV4SignerAuth(boto3.Session().get_credentials(), REGION, SERVICE)

os_client = OpenSearch(
    hosts=[{"host": HOST, "port": 443}],
    http_auth=auth,
    use_ssl=True, verify_certs=True,
    connection_class=RequestsHttpConnection,
)

bedrock = boto3.client("bedrock-runtime", region_name=REGION)
MODEL_ID = "amazon.titan-embed-text-v2:0"
ddb = boto3.resource("dynamodb", region_name=REGION).Table(os.getenv("DDB_TABLE", "Courses"))

def embed_text(text: str) -> list[float]:
    """Generate embeddings using Titan v2"""
    payload = {"inputText": text}
    resp = bedrock.invoke_model(
        modelId=MODEL_ID,
        contentType="application/json",
        accept="application/json",
        body=json.dumps(payload),
    )
    body = json.loads(resp["body"].read())
    return body["embedding"]



@mcp.tool()
async def external_search_courses(keyword: str) -> dict:
    """If the agent cannot find enough relevant course from our internal vector database, then use 
    this function to search on the external online platforms including coursera, udemy, edx
    
    Args:
        keyword: the keyword used to search for (e.g. 'python', 'programming', 'AI', 'business')
    
    Returns:
        list: a list of dictionary containing the information relevant course elements of each course
    
    Examples:
        external_search_courses( 'python')
        external_search_courses('data science')
        external_search_courses('machine learning')
    """
    logger.info(f"external_vector_search_courses called with query: '{keyword}'")

    edx_scraper = EdxScraper()
    edx_resp = edx_scraper.query(keyword)
    edx_course_info = edx_scraper.handle_response(edx_resp)
    print(f'number of course found from edx: {len(edx_course_info)}')
    coursera_scraper = CourseraScraper()
    coursera_resp = coursera_scraper.query(keyword)
    coursera_course_info = coursera_scraper.handle_response(coursera_resp)
    print(f'number of course found from Coursera: {len(coursera_course_info)}')

    udemy_scraper = UdemyScraper()
    udemy_resp = udemy_scraper.query(keyword)
    udemy_course_info = udemy_scraper.handle_response(udemy_resp)
    print(f'number of course found from Udemy: {len(udemy_course_info)}')

    course_info = edx_course_info + coursera_course_info + udemy_course_info
    store = CourseStore()
    store.put_many(course_info)


    logger.info(f"external_vector_search_courses completed: {len(course_info)} courses found ")

    course_info = edx_course_info[:3] + coursera_course_info[:3] + udemy_course_info[:3]

    return course_info

@mcp.tool()
async def get_course_details_by_uuid(course_uuid: str) -> dict:
    """
    Extract detailed course information from DynamoDB by course UUID.
    Use this tool when you need to get complete information about a specific course.
    
    Args:
        course_uuid: The unique identifier of the course
    
    Returns:
        dict: Complete course details from database
    
    Examples:
        get_course_details_by_uuid('12345-abcd-6789-efgh')
    """
    logger.info(f"get_course_details_by_uuid called with course_uuid: '{course_uuid}'")
    
    try:
        # Fetch course details from DynamoDB
        response = ddb.get_item(Key={"uuid": course_uuid})
        
        if "Item" in response:
            course_data = response["Item"]
            logger.info(f"Course details found for UUID: {course_uuid}")
            return {
                "success": True,
                "course": course_data
            }
        else:
            logger.warning(f"No course found for UUID: {course_uuid}")
            return {
                "success": False,
                "error": f"No course found with UUID: {course_uuid}",
                "course": None
            }
            
    except Exception as e:
        logger.error(f"Error fetching course details for UUID {course_uuid}: {e}")
        return {
            "success": False,
            "error": f"Database error: {str(e)}",
            "course": None
        }

@mcp.tool()
async def internal_vector_search_courses(query: str, k: int = 5) -> dict:
    """
    Summarise the user query base on their needs of training and pass it to this function carry the vector search
    to extract the most relevant course information from our database. If not sufficient courses are returned to can
    move on to call another tool, i.e. external_search_courses, to search from online
    Args:
        query: summarised query from user
        k: number of similar courses to return (default: 5)
    
    Returns:
        dict: containing 'courses' list with full course details and similarity scores
    
    Examples:
        internal_vector_search_courses('design ai agent with MCP, intermediate level')
        internal_vector_search_courses('use langgraph to build multi agent workflow, intermediate level')
        internal_vector_search_courses('learn the foundation of the AI and machine learning. beginner level')
    """

    logger.info(f"internal_vector_search_courses called with query: '{query}', k: {k}")

    try:
        # 1. Generate embedding for the query
        query_vector = embed_text(query)
        
        # 2. Perform vector similarity search
        search_body = {
            "query": {
                "knn": {
                    "vector": {
                        "vector": query_vector,
                        "k": k
                    }
                }
            },
            "_source": ["uuid", "title", "subject_primary", "partner_primary", "level", "skills"],
            "size": k
        }
        
        response = os_client.search(index=INDEX, body=search_body)
        
        # 3. Get similar course UUIDs and scores
        similar_courses = [
            {
                "uuid": hit["_source"]["uuid"],
                "score": hit["_score"],
                "title": hit["_source"]["title"],
                "subject_primary": hit["_source"]["subject_primary"],
                "partner_primary": hit["_source"]["partner_primary"],
                "level": hit["_source"]["level"],
                "skills": hit["_source"]["skills"]
            }
            for hit in response["hits"]["hits"]
        ]
        
        # 4. Fetch full course details from DynamoDB
        course_details = []
        for course in similar_courses:
            try:
                full_course = ddb.get_item(Key={"uuid": course["uuid"]})
                if "Item" in full_course:
                    course_data = full_course["Item"]
                    course_data["similarity_score"] = course["score"]
                    course_details.append(course_data)
                else:
                    print(f"Course {course['uuid']} not found in DynamoDB")
            except Exception as e:
                print(f"Error fetching course {course['uuid']} from DynamoDB: {e}")
        
        logger.info(f"internal_vector_search_courses completed: {len(course_details)} courses found for query '{query}'")

        return {
            "success": True,
            "query": query,
            "total_results": len(course_details),
            "courses": course_details
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Vector search failed: {str(e)}",
            "query": query,
            "courses": []
        }

@mcp.tool()
async def get_recommended_course_details(course_uuids: list) -> dict:
    """
    Get detailed information for recommended courses by their UUIDs.
    Call this tool when you finish recommending the course to the user use this call to pass the final courses structured information to the backend
    
    Args:
        course_uuids: List of course UUIDs to get details for
    
    Returns:
        dict: Complete course details for frontend visualization
    
    Examples:
        get_recommended_course_details(['course-123', 'course-456'])
    """
    logger.info(f"get_recommended_course_details called with {len(course_uuids)} course UUIDs")
    
    try:
        course_details = []
        
        for course_uuid in course_uuids:
            try:
                # Fetch course details from DynamoDB
                response = ddb.get_item(Key={"uuid": course_uuid})
                
                if "Item" in response:
                    course_data = response["Item"]
                    course_details.append(course_data)
                    logger.info(f"Found course: {course_data.get('title', course_uuid)}")
                else:
                    logger.warning(f"Course not found: {course_uuid}")
                    
            except Exception as e:
                logger.error(f"Error fetching course {course_uuid}: {e}")
        
        logger.info(f"get_recommended_course_details completed: {len(course_details)} courses retrieved")
        
        return {
            "success": True,
            "courses": course_details,
            "total_results": len(course_details),
            "course_uuids_requested": course_uuids
        }
        
    except Exception as e:
        logger.error(f"Error in get_recommended_course_details: {e}")
        return {
            "success": False,
            "error": str(e),
            "courses": [],
            "course_uuids_requested": course_uuids
        }

if __name__ == '__main__':
    mcp.run()
