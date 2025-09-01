from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Models
class CourseSearchRequest(BaseModel):
    query: str
    k: int = 10

class Course(BaseModel):
    uuid: str
    title: str
    provider: str
    level: str
    skills: List[str]
    description: str
    similarity_score: float = 0.0

class CourseSearchResponse(BaseModel):
    success: bool
    courses: List[Course]
    total_results: int
    query: str
    error: Optional[str] = None

class StudyPlanRequest(BaseModel):
    courses: List[Dict[str, Any]]
    userId: str

class StudyPlanResponse(BaseModel):
    success: bool
    message: str
    courses_count: int = 0

# Create FastAPI app
app = FastAPI(
    title="Grace Papers Backend API",
    description="AI Learning Platform Backend with Environment Variables",
    version="1.0.0"
)

# Configure CORS with environment variables
allowed_origins = os.getenv('CORS_ORIGINS', '*').split(',') if os.getenv('CORS_ORIGINS') else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# AWS Service Class with Environment Variables
class AWSService:
    def __init__(self):
        self.dynamodb = None
        self.opensearch = None
        self.initialized = False
        self.table_name = os.getenv('DDB_TABLE', 'Courses')
        self.aws_region = os.getenv('AWS_REGION', 'ap-southeast-2')
        self.os_endpoint = os.getenv('OS_ENDPOINT')
        
    async def initialize(self):
        """Initialize AWS services using environment variables"""
        try:
            # Get AWS credentials from environment
            aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
            aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
            
            if not aws_access_key or not aws_secret_key:
                logger.warning("⚠️ AWS credentials not found in environment variables")
                logger.info("📝 Using mock data. Add AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY to enable real data")
                return False
            
            # Initialize AWS services
            import boto3
            
            # Initialize DynamoDB
            self.dynamodb = boto3.resource(
                'dynamodb',
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=self.aws_region
            )
            
            # Test DynamoDB connection
            table = self.dynamodb.Table(self.table_name)
            table.load()
            logger.info(f"✅ Connected to DynamoDB table: {self.table_name}")
            
            # Initialize OpenSearch if endpoint is provided
            if self.os_endpoint:
                try:
                    from opensearchpy import OpenSearch, RequestsHttpConnection
                    from requests_aws4auth import AWS4Auth
                    
                    # Create AWS4Auth for OpenSearch
                    awsauth = AWS4Auth(
                        aws_access_key,
                        aws_secret_key,
                        self.aws_region,
                        'es'  # service name for OpenSearch/Elasticsearch
                    )
                    
                    self.opensearch = OpenSearch(
                        hosts=[{'host': self.os_endpoint.replace('https://', '').replace('http://', ''), 'port': 443}],
                        http_auth=awsauth,
                        use_ssl=True,
                        verify_certs=True,
                        connection_class=RequestsHttpConnection
                    )
                    
                    # Test OpenSearch connection
                    self.opensearch.info()
                    logger.info(f"✅ Connected to OpenSearch: {self.os_endpoint}")
                    
                except ImportError as e:
                    logger.warning(f"OpenSearch dependencies missing: {e}")
                    logger.info("Install: pip install opensearch-py requests-aws4auth")
                except Exception as e:
                    logger.warning(f"OpenSearch connection failed: {e}")
            
            self.initialized = True
            logger.info("✅ AWS services initialized successfully")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize AWS services: {e}")
            logger.info("📝 Falling back to mock data")
            return False
    
    async def search_courses(self, query: str, k: int = 10):
        """Search courses using AWS services or return mock data"""
        if not self.initialized:
            logger.info(f"🔍 Searching with mock data for: '{query}'")
            return self._get_mock_courses(query, k)
        
        try:
            courses = []
            
            # Try OpenSearch first (better for text search)
            if self.opensearch:
                courses = await self._search_opensearch(query, k)
            
            # Fallback to DynamoDB if OpenSearch didn't return enough results
            if len(courses) < k and self.dynamodb:
                ddb_courses = await self._search_dynamodb(query, k - len(courses))
                courses.extend(ddb_courses)
            
            if courses:
                logger.info(f"✅ Found {len(courses)} courses from AWS for query: '{query}'")
                return {
                    'success': True,
                    'courses': courses,
                    'total_results': len(courses),
                    'query': query
                }
            else:
                logger.info(f"📝 No AWS results for '{query}', using mock data")
                return self._get_mock_courses(query, k)
            
        except Exception as e:
            logger.error(f"❌ Error searching AWS services: {e}")
            return self._get_mock_courses(query, k)
    
    async def _search_opensearch(self, query: str, k: int):
        """Search in OpenSearch"""
        try:
            index_name = os.getenv('OS_INDEX', 'courses')
            
            search_body = {
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["title^2", "description", "skills"]
                    }
                },
                "size": k
            }
            
            response = self.opensearch.search(
                index=index_name,
                body=search_body
            )
            
            courses = []
            for hit in response['hits']['hits']:
                source = hit['_source']
                course = {
                    'uuid': source.get('uuid', hit['_id']),
                    'title': source.get('title', 'Unknown Course'),
                    'provider': source.get('partner', source.get('provider', 'Unknown')),
                    'level': source.get('level', 'Beginner'),
                    'skills': source.get('skills', [query]),
                    'description': source.get('description', ''),
                    'similarity_score': hit['_score'] / 10.0  # Normalize score
                }
                courses.append(course)
            
            return courses
            
        except Exception as e:
            logger.error(f"OpenSearch error: {e}")
            return []
    
    async def _search_dynamodb(self, query: str, k: int):
        """Search in DynamoDB"""
        try:
            table = self.dynamodb.Table(self.table_name)
            
            # Use GSI if available, otherwise scan
            try:
                # Try to search by subject first (if you have a subject GSI)
                response = table.query(
                    IndexName='SubjectIndex',
                    KeyConditionExpression=boto3.dynamodb.conditions.Key('subject').eq(query),
                    Limit=k
                )
                items = response.get('Items', [])
            except:
                # Fallback to scan with filter
                response = table.scan(
                    FilterExpression=boto3.dynamodb.conditions.Attr('title').contains(query) | 
                                   boto3.dynamodb.conditions.Attr('description').contains(query),
                    Limit=k
                )
                items = response.get('Items', [])
            
            courses = []
            for item in items:
                course = {
                    'uuid': str(item.get('uuid', '')),
                    'title': str(item.get('title', '')),
                    'provider': str(item.get('partner', item.get('provider', 'Unknown'))),
                    'level': str(item.get('level', 'Beginner')),
                    'skills': item.get('skills', [query]) if isinstance(item.get('skills'), list) else [query],
                    'description': str(item.get('description', '')),
                    'similarity_score': 0.8
                }
                courses.append(course)
            
            return courses
            
        except Exception as e:
            logger.error(f"DynamoDB error: {e}")
            return []
    
    def _get_mock_courses(self, query: str, k: int):
        """Generate mock courses based on query"""
        # More realistic mock data based on common course topics
        course_templates = [
            {
                "title": f"{query.title()} Fundamentals",
                "provider": "TechEd University",
                "level": "Beginner",
                "description": f"Master the fundamentals of {query} with hands-on projects and real-world examples."
            },
            {
                "title": f"Advanced {query.title()} Techniques",
                "provider": "Professional Academy",
                "level": "Advanced", 
                "description": f"Advanced concepts and industry best practices in {query}."
            },
            {
                "title": f"{query.title()} for Beginners",
                "provider": "Learning Hub",
                "level": "Beginner",
                "description": f"Complete beginner's guide to {query} - no prior experience needed."
            },
            {
                "title": f"Practical {query.title()} Applications",
                "provider": "Industry Institute",
                "level": "Intermediate",
                "description": f"Learn {query} through practical projects and case studies."
            },
            {
                "title": f"{query.title()} Certification Prep",
                "provider": "Cert Academy",
                "level": "Intermediate",
                "description": f"Prepare for {query} certification exams with comprehensive coverage."
            }
        ]
        
        mock_courses = []
        for i in range(min(k, len(course_templates))):
            template = course_templates[i]
            course = {
                "uuid": f"mock-{query.lower().replace(' ', '-')}-{i+1}",
                "title": template["title"],
                "provider": template["provider"],
                "level": template["level"],
                "skills": [query.title(), "Practice", "Application"],
                "description": template["description"],
                "similarity_score": 0.9 - (i * 0.1)
            }
            mock_courses.append(course)
        
        # Fill remaining slots if needed
        while len(mock_courses) < k:
            i = len(mock_courses)
            mock_courses.append({
                "uuid": f"mock-{query.lower().replace(' ', '-')}-{i+1}",
                "title": f"{query.title()} Course {i+1}",
                "provider": "Online Learning",
                "level": ["Beginner", "Intermediate", "Advanced"][i % 3],
                "skills": [query.title(), "Learning"],
                "description": f"Learn {query} with structured lessons and practical exercises.",
                "similarity_score": max(0.1, 0.9 - (i * 0.1))
            })
        
        return {
            "success": True,
            "courses": mock_courses,
            "total_results": len(mock_courses),
            "query": query
        }

# Global AWS service instance
aws_service = AWSService()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("🚀 Starting Grace Papers Backend...")
    logger.info(f"Environment: {os.getenv('VERCEL_ENV', 'development')}")
    logger.info(f"DynamoDB Table: {aws_service.table_name}")
    logger.info(f"AWS Region: {aws_service.aws_region}")
    
    if aws_service.os_endpoint:
        logger.info(f"OpenSearch Endpoint: {aws_service.os_endpoint}")
    else:
        logger.info("OpenSearch: Not configured")
    
    await aws_service.initialize()

# Health check
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "Grace Papers Backend is running",
        "aws_initialized": aws_service.initialized,
        "environment": os.getenv('VERCEL_ENV', 'development'),
        "version": "1.0.0",
        "services": {
            "dynamodb": aws_service.dynamodb is not None,
            "opensearch": aws_service.opensearch is not None,
            "table_name": aws_service.table_name
        }
    }

# Test endpoint
@app.get("/api/test")
async def simple_test():
    return {
        "message": "Server is working!",
        "timestamp": datetime.now().isoformat(),
        "aws_available": aws_service.initialized,
        "environment": os.getenv("VERCEL_ENV", "development"),
        "config": {
            "aws_region": aws_service.aws_region,
            "table_name": aws_service.table_name,
            "has_opensearch": bool(aws_service.os_endpoint)
        }
    }

# Course search endpoint
@app.post("/api/search-courses", response_model=CourseSearchResponse)
async def search_courses(request: CourseSearchRequest):
    """Search for courses using AWS services or mock data"""
    logger.info(f"🔍 Course search request: '{request.query}' (limit: {request.k})")
    
    try:
        result = await aws_service.search_courses(request.query, request.k)
        
        courses = [Course(**course_data) for course_data in result["courses"]]
        
        logger.info(f"✅ Returning {len(courses)} courses for '{request.query}'")
        
        return CourseSearchResponse(
            success=result["success"],
            courses=courses,
            total_results=result["total_results"],
            query=result["query"]
        )
        
    except Exception as e:
        logger.error(f"❌ Error in search_courses: {e}")
        return CourseSearchResponse(
            success=False,
            courses=[],
            total_results=0,
            query=request.query,
            error=str(e)
        )

# Save study plan endpoint
@app.post("/api/save-study-plan", response_model=StudyPlanResponse)
async def save_study_plan(request: StudyPlanRequest):
    """Save study plan for a user"""
    logger.info(f"💾 Saving study plan for user {request.userId} with {len(request.courses)} courses")
    
    try:
        # For now, just return success - you can add actual saving logic later
        return StudyPlanResponse(
            success=True,
            message=f"Study plan saved successfully for user {request.userId}",
            courses_count=len(request.courses)
        )
    except Exception as e:
        logger.error(f"❌ Error saving study plan: {e}")
        return StudyPlanResponse(
            success=False,
            message="Failed to save study plan",
            courses_count=0
        )

# User profile endpoint
@app.get("/api/user-profile/{user_id}")
async def get_user_profile(user_id: str):
    """Get user profile"""
    return {
        "success": True,
        "profile": {
            "id": user_id,
            "name": "Demo User",
            "role": "Learner", 
            "experience": "Beginner",
            "goals": ["Skill Development", "Career Growth"],
            "completedCourses": 2,
            "totalHours": 16
        }
    }

# Study plan endpoint
@app.get("/api/study-plan/{user_id}")
async def get_study_plan(user_id: str):
    """Get user's study plan"""
    return {
        "success": True,
        "study_plan": [],
        "user_id": user_id
    }

# Course details endpoint
@app.get("/api/course/{course_id}")
async def get_course_details(course_id: str):
    """Get detailed information about a specific course"""
    return {
        "success": True,
        "course": {
            "uuid": course_id,
            "title": f"Course: {course_id}",
            "description": "Detailed course information with curriculum and objectives",
            "provider": "Learning Provider",
            "level": "Intermediate",
            "skills": ["Core Skills", "Advanced Techniques"],
            "duration": "6 weeks",
            "rating": 4.5,
            "url": f"https://example.com/course/{course_id}"
        }
    }

# Environment info endpoint (for debugging)
@app.get("/api/debug/env")
async def debug_environment():
    """Debug endpoint to check environment configuration (safe values only)"""
    return {
        "vercel_env": os.getenv("VERCEL_ENV", "not-set"),
        "aws_region": os.getenv("AWS_REGION", "not-set"),
        "ddb_table": os.getenv("DDB_TABLE", "not-set"),
        "has_aws_access_key": bool(os.getenv("AWS_ACCESS_KEY_ID")),
        "has_aws_secret_key": bool(os.getenv("AWS_SECRET_ACCESS_KEY")),
        "has_os_endpoint": bool(os.getenv("OS_ENDPOINT")),
        "cors_origins": os.getenv("CORS_ORIGINS", "not-set")
    }

# Export for Vercel
def handler(event, context):
    return app
