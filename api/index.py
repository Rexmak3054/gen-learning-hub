from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os

# Simple Pydantic models
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

# Create FastAPI app
app = FastAPI(
    title="Grace Papers Backend API",
    description="AI Learning Platform Backend",
    version="1.0.0"
)

# Configure CORS for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your actual domains
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Health check
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "Grace Papers Backend is running on Vercel",
        "version": "1.0.0"
    }

# Test endpoint
@app.get("/api/test")
async def simple_test():
    return {
        "message": "Server is working on Vercel!",
        "timestamp": datetime.now().isoformat(),
        "environment": "production"
    }

# Mock course search for initial deployment
@app.post("/api/search-courses", response_model=CourseSearchResponse)
async def search_courses(request: CourseSearchRequest):
    """Mock course search endpoint"""
    
    # Mock courses based on query
    mock_courses = [
        {
            "uuid": f"course-{i+1}",
            "title": f"{request.query.title()} Course {i+1}",
            "provider": "Online University",
            "level": ["Beginner", "Intermediate", "Advanced"][i % 3],
            "skills": [request.query.title(), "Learning", "Practice"],
            "description": f"A comprehensive course about {request.query} covering fundamental concepts and practical applications.",
            "similarity_score": 0.9 - (i * 0.1)
        }
        for i in range(min(request.k, 5))  # Return max 5 courses for demo
    ]
    
    courses = [Course(**course_data) for course_data in mock_courses]
    
    return CourseSearchResponse(
        success=True,
        courses=courses,
        total_results=len(courses),
        query=request.query
    )

# User endpoints
@app.get("/api/user-profile/{user_id}")
async def get_user_profile(user_id: str):
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

# For Vercel
def handler(event, context):
    """AWS Lambda handler for Vercel"""
    return app

# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
