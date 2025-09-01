from pydantic import BaseModel, Field, validator
from typing import List, Optional, Any, Dict
from datetime import datetime

class CourseSearchRequest(BaseModel):
    """Request model for course search"""
    query: str = Field(..., description="Search query for courses", min_length=1)
    k: int = Field(10, description="Number of courses to return", ge=1, le=50)

class Course(BaseModel):
    """Course model"""
    uuid: str
    title: str
    provider: str
    level: str
    skills: List[str]
    description: str
    similarity_score: Optional[float] = None
    duration: Optional[str] = None
    rating: Optional[float] = None
    url: Optional[str] = None

class CourseSearchResponse(BaseModel):
    """Response model for course search"""
    success: bool
    courses: List[Course]
    total_results: int
    query: str
    error: Optional[str] = None

class StudyPlanRequest(BaseModel):
    """Request model for saving study plan"""
    courses: List[Dict[str, Any]]
    userId: str = Field(..., description="User ID")

class StudyPlanResponse(BaseModel):
    """Response model for study plan operations"""
    success: bool
    message: str
    courses_count: Optional[int] = None
    error: Optional[str] = None

class UserProfile(BaseModel):
    """User profile model"""
    id: str
    name: str
    role: str
    experience: str
    goals: List[str]
    completedCourses: int
    totalHours: int

class UserProfileResponse(BaseModel):
    """Response model for user profile"""
    success: bool
    profile: Optional[UserProfile] = None
    error: Optional[str] = None

class StudyPlan(BaseModel):
    """Study plan model"""
    user_id: str
    courses: List[Course]
    created_at: datetime
    updated_at: datetime

class StudyPlanGetResponse(BaseModel):
    """Response model for getting study plan"""
    success: bool
    study_plan: List[Dict[str, Any]]
    user_id: str
    error: Optional[str] = None

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    message: str
    version: str

class ErrorResponse(BaseModel):
    """Generic error response"""
    success: bool = False
    error: str
    detail: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "success": False,
                "error": "Something went wrong", 
                "detail": "More specific error information"
            }
        }
