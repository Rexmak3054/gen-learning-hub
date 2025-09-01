# Grace Papers FastAPI Backend

This is the FastAPI backend for the Grace Papers AI Learning Platform. It provides REST endpoints for course search and user management, powered by a research agent that uses LangGraph and MCP tools.

## 🏗️ Architecture

```
backend/
├── main.py                   # FastAPI application entry point
├── requirements.txt          # Python dependencies
├── start.sh                 # Startup script
├── .env.example             # Environment variables template
└── app/
    ├── __init__.py
    ├── models/
    │   ├── __init__.py
    │   └── schemas.py        # Pydantic models
    ├── routes/
    │   ├── __init__.py
    │   ├── courses.py        # Course-related endpoints
    │   └── users.py          # User-related endpoints
    └── services/
        ├── __init__.py
        └── research_agent.py  # Research agent service
```

## 🚀 Quick Start

1. **Setup Environment**
   ```bash
   cd backend
   chmod +x start.sh
   ./start.sh
   ```

2. **Configure Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env with your actual values (OpenAI API key, AWS credentials, etc.)
   ```

3. **Start the Server**
   ```bash
   uvicorn main:app --reload
   ```

The FastAPI backend will start on `http://localhost:8000`

## 📖 API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 📡 API Endpoints

### Course Management

#### Search Courses
```http
POST /api/search-courses
Content-Type: application/json

{
  "query": "python programming",
  "k": 10
}
```

**Response:**
```json
{
  "success": true,
  "courses": [
    {
      "uuid": "course-123",
      "title": "Python Programming Fundamentals",
      "provider": "Coursera",
      "level": "Beginner",
      "skills": ["Python", "Programming"],
      "description": "Learn Python programming from scratch",
      "similarity_score": 0.95
    }
  ],
  "total_results": 1,
  "query": "python programming"
}
```

#### Save Study Plan
```http
POST /api/save-study-plan
Content-Type: application/json

{
  "courses": [...],
  "userId": "user-123"
}
```

#### Get Course Details
```http
GET /api/course/{course_id}
```

### User Management

#### Get User Profile
```http
GET /api/user-profile/{userId}
```

#### Get Study Plan
```http
GET /api/study-plan/{userId}
```

#### Update User Profile
```http
PUT /api/user-profile/{userId}
Content-Type: application/json

{
  "name": "John Doe",
  "role": "Developer",
  "experience": "Intermediate"
}
```

### Health Checks
- **General Health**: `GET /health`
- **Course Service Health**: `GET /api/courses/health`
- **User Service Health**: `GET /api/users/health`

## 🤖 Research Agent

The research agent is the core component that:
- Uses **LangGraph** for workflow orchestration
- Integrates with **MCP tools** for course searching
- Provides intelligent course recommendations
- Handles both internal vector search and external API calls
- Runs **asynchronously** with FastAPI

### Research Agent Features:
- **Auto-initialization**: Lazy loads on first request
- **Tool Integration**: Connects to your existing `course_server.py`
- **Error Handling**: Graceful fallbacks and error reporting
- **Structured Responses**: Returns properly formatted course data

## 🔧 Configuration

Key environment variables:
- `OPENAI_API_KEY`: Required for the research agent LLM
- `AWS_*`: AWS credentials for your existing MCP tools
- `PORT`: Server port (default: 8000)
- `DEBUG`: Enable debug mode
- `LOG_LEVEL`: Logging level (INFO, DEBUG, WARNING, ERROR)

## 🔗 Integration with Frontend

Update your frontend's environment variables:

```bash
# frontend/.env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENABLE_MOCK_DATA=false
```

The FastAPI backend is fully compatible with your existing React frontend service calls.

## 🛠️ Development

### Run in Development Mode
```bash
uvicorn main:app --reload --log-level debug
```

### Testing Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Course search
curl -X POST "http://localhost:8000/api/search-courses" \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning", "k": 5}'

# Research agent health
curl http://localhost:8000/api/courses/health
```

### Features

- **Automatic API Documentation**: Visit `/docs` for interactive API testing
- **Type Safety**: Pydantic models ensure request/response validation
- **Async Support**: Native async/await support for better performance
- **CORS Configured**: Ready for frontend integration
- **Structured Logging**: Comprehensive logging for debugging
- **Error Handling**: Proper HTTP status codes and error messages

## 🔄 Migration from Flask

The FastAPI backend is a complete replacement for the Flask version with these improvements:

- ✅ **Better Async Support**: Native async/await
- ✅ **Auto Documentation**: Interactive API docs
- ✅ **Type Safety**: Pydantic models for validation
- ✅ **Better Performance**: Faster request handling
- ✅ **Modern Standards**: OpenAPI 3.0 compliance

## 🚨 Important Notes

1. **Research Agent Path**: Make sure your `course_server.py` is accessible from the backend directory
2. **Environment Setup**: Configure all AWS credentials and OpenSearch endpoints correctly
3. **OpenAI API**: Ensure your OpenAI API key is set for the research agent
4. **Port Change**: Default port is now 8000 (instead of Flask's 5000)

## 📝 Next Steps

1. **Configure Environment**: Set up your `.env` file with real credentials
2. **Test Health Endpoint**: Verify the server starts correctly
3. **Test Research Agent**: Try the course search endpoint
4. **Update Frontend**: Change API URL to point to port 8000
5. **Enhance Course Parsing**: Improve course data extraction from MCP tools
6. **Add Database**: Implement persistent storage for study plans and user profiles

## 🐛 Troubleshooting

### Research Agent Not Initializing
- Check that `course_server.py` exists in the parent directory
- Verify OpenAI API key is set correctly
- Check AWS credentials for MCP tools

### CORS Issues
- Ensure your frontend URL is in the CORS origins list
- Check that requests include proper headers

### Port Conflicts
- Change the port in `.env` if 8000 is already in use
- Update your frontend's `REACT_APP_API_URL` accordingly
