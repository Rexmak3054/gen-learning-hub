#!/usr/bin/env python3
"""
Debug script to find where model_validator import is coming from
"""

import sys
import traceback

def test_imports():
    print("🔍 Testing imports step by step...")
    
    # Test basic imports first
    try:
        import pydantic
        print(f"✅ pydantic version: {pydantic.__version__}")
    except Exception as e:
        print(f"❌ pydantic import failed: {e}")
        return
    
    try:
        from pydantic import BaseModel, Field
        print("✅ pydantic BaseModel, Field imported")
    except Exception as e:
        print(f"❌ pydantic BaseModel import failed: {e}")
        return
    
    try:
        from fastapi import FastAPI
        print("✅ FastAPI imported")
    except Exception as e:
        print(f"❌ FastAPI import failed: {e}")
        print("Full traceback:")
        traceback.print_exc()
        return
    
    try:
        from app.models.schemas import CourseSearchRequest
        print("✅ Local schemas imported")
    except Exception as e:
        print(f"❌ Local schemas import failed: {e}")
        print("Full traceback:")
        traceback.print_exc()
        return
        
    try:
        from app.routes.courses import router
        print("✅ Course routes imported")
    except Exception as e:
        print(f"❌ Course routes import failed: {e}")
        print("Full traceback:")
        traceback.print_exc()
        return
        
    try:
        from app.services.research_agent import get_research_agent
        print("✅ Research agent imported")
    except Exception as e:
        print(f"❌ Research agent import failed: {e}")
        print("Full traceback:")
        traceback.print_exc()
        return
    
    print("🎉 All imports successful!")

if __name__ == "__main__":
    test_imports()
