from fastapi import APIRouter, HTTPException, status
from app.models.schemas import (
    CourseSearchRequest, 
    CourseSearchResponse, 
    StudyPlanRequest, 
    StudyPlanResponse,
    ErrorResponse
)
from app.services.research_agent import get_research_agent
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post(
    "/search-courses",
    response_model=CourseSearchResponse,
    summary="Search for courses",
    description="Search for courses using the AI research agent with vector search and external APIs"
)
async def search_courses(request: CourseSearchRequest):
    """
    Search for courses using the research agent
    
    - **query**: Search query for courses (e.g., "python programming", "data science")
    - **k**: Number of courses to return (1-50, default: 10)
    """
    try:
        logger.info(f"Course search request: query='{request.query}', k={request.k}")
        
        # Get the research agent
        agent = await get_research_agent()
        
        # Search for courses
        result = await agent.search_courses(request.query, request.k)
        
        if result.success:
            logger.info(f"Course search successful: {result.total_results} courses found")
            return CourseSearchResponse(
                success=result.success,
                courses=result.courses,
                total_results=result.total_results,
                query=result.search_query
            )
        else:
            logger.error(f"Course search failed: {result.error}")
            return CourseSearchResponse(
                success=False,
                courses=[],
                total_results=0,
                query=request.query,
                error=result.error
            )
        
    except Exception as e:
        logger.error(f"Error in search_courses endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.post(
    "/save-study-plan",
    response_model=StudyPlanResponse,
    summary="Save user study plan",
    description="Save a user's selected courses as a study plan"
)
async def save_study_plan(request: StudyPlanRequest):
    """
    Save a user's study plan
    
    - **courses**: List of selected courses
    - **userId**: User identifier
    """
    try:
        logger.info(f"Saving study plan for user {request.userId} with {len(request.courses)} courses")
        
        # TODO: Implement actual saving logic (database, file, etc.)
        # For now, we'll just return success
        
        return StudyPlanResponse(
            success=True,
            message=f"Study plan saved successfully for user {request.userId}",
            courses_count=len(request.courses)
        )
        
    except Exception as e:
        logger.error(f"Error in save_study_plan endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get(
    "/course/{course_id}",
    summary="Get course details",
    description="Get detailed information about a specific course"
)
async def get_course_details(course_id: str):
    """
    Get detailed information about a specific course
    
    - **course_id**: Unique course identifier
    """
    try:
        logger.info(f"Fetching details for course: {course_id}")
        
        # TODO: Implement actual course detail fetching
        # This would typically query your database or external APIs
        
        return {
            "success": True,
            "course": {
                "uuid": course_id,
                "title": f"Course Details for {course_id}",
                "description": "Detailed course information would be fetched here",
                "provider": "TBD",
                "level": "TBD",
                "skills": [],
                "duration": "TBD",
                "rating": None,
                "url": None
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching course details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get(
    "/courses/health",
    summary="Course service health check"
)
async def courses_health_check():
    """Health check for the course service and research agent"""
    try:
        agent = await get_research_agent()
        return {
            "status": "healthy",
            "research_agent_initialized": agent.initialized,
            "tools_loaded": len(agent.tools) if agent.tools else 0
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "research_agent_initialized": False,
            "tools_loaded": 0
        }
