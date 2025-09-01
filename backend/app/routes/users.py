from fastapi import APIRouter, HTTPException, status
from app.models.schemas import (
    UserProfileResponse, 
    StudyPlanGetResponse,
    UserProfile
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get(
    "/user-profile/{user_id}",
    response_model=UserProfileResponse,
    summary="Get user profile",
    description="Get user profile information by user ID"
)
async def get_user_profile(user_id: str):
    """
    Get user profile information
    
    - **user_id**: Unique user identifier
    """
    try:
        logger.info(f"Fetching profile for user: {user_id}")
        
        # TODO: Implement actual user profile fetching from database
        # For now, return mock data matching your frontend expectations
        
        mock_profile = UserProfile(
            id=user_id,
            name="Sarah Chen",
            role="Marketing Manager", 
            experience="Beginner",
            goals=["AI Tools Proficiency", "Data Analysis", "Automation"],
            completedCourses=3,
            totalHours=24
        )
        
        return UserProfileResponse(
            success=True,
            profile=mock_profile
        )
        
    except Exception as e:
        logger.error(f"Error fetching user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get(
    "/study-plan/{user_id}",
    response_model=StudyPlanGetResponse,
    summary="Get user study plan",
    description="Get user's saved study plan by user ID"
)
async def get_study_plan(user_id: str):
    """
    Get user's saved study plan
    
    - **user_id**: Unique user identifier
    """
    try:
        logger.info(f"Fetching study plan for user: {user_id}")
        
        # TODO: Implement actual study plan fetching from database
        # For now, return empty study plan
        
        return StudyPlanGetResponse(
            success=True,
            study_plan=[],
            user_id=user_id
        )
        
    except Exception as e:
        logger.error(f"Error fetching study plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.put(
    "/user-profile/{user_id}",
    summary="Update user profile",
    description="Update user profile information"
)
async def update_user_profile(user_id: str, profile_data: dict):
    """
    Update user profile information
    
    - **user_id**: Unique user identifier
    - **profile_data**: Profile data to update
    """
    try:
        logger.info(f"Updating profile for user: {user_id}")
        
        # TODO: Implement actual profile updating logic
        
        return {
            "success": True,
            "message": f"Profile updated successfully for user {user_id}",
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.delete(
    "/study-plan/{user_id}",
    summary="Clear user study plan",
    description="Clear/delete user's study plan"
)
async def clear_study_plan(user_id: str):
    """
    Clear user's study plan
    
    - **user_id**: Unique user identifier
    """
    try:
        logger.info(f"Clearing study plan for user: {user_id}")
        
        # TODO: Implement actual study plan clearing logic
        
        return {
            "success": True,
            "message": f"Study plan cleared for user {user_id}",
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"Error clearing study plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get(
    "/users/health",
    summary="User service health check"
)
async def users_health_check():
    """Health check for the user service"""
    return {
        "status": "healthy",
        "service": "users",
        "endpoints": [
            "GET /api/user-profile/{user_id}",
            "GET /api/study-plan/{user_id}",
            "PUT /api/user-profile/{user_id}",
            "DELETE /api/study-plan/{user_id}"
        ]
    }
