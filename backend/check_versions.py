#!/usr/bin/env python3
"""
Check current package versions to ensure compatibility
"""
import sys

def check_package_version(package_name):
    try:
        module = __import__(package_name)
        version = getattr(module, '__version__', 'Unknown')
        print(f"✅ {package_name}: {version}")
        return version
    except ImportError:
        print(f"❌ {package_name}: Not installed")
        return None

def main():
    print("🔍 Checking package versions...")
    print("=" * 40)
    
    packages = [
        'pydantic',
        'fastapi', 
        'uvicorn',
        'langchain',
        'langchain_core',
        'langchain_openai',
        'langgraph',
        'mcp'
    ]
    
    for package in packages:
        check_package_version(package)
    
    print("\n🧪 Testing critical imports...")
    
    try:
        from pydantic import BaseModel, Field
        print("✅ Pydantic imports successful")
    except ImportError as e:
        print(f"❌ Pydantic import failed: {e}")
    
    try:
        from fastapi import FastAPI
        print("✅ FastAPI import successful")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        
    try:
        from langchain_core.messages import HumanMessage
        print("✅ LangChain core imports successful")
    except ImportError as e:
        print(f"❌ LangChain core import failed: {e}")

if __name__ == "__main__":
    main()
