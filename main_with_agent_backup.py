from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import os
import logging
import asyncio
import uuid
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple Pydantic models (v1 compatible)
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

# Chat-related models
class ChatMessage(BaseModel):
    id: str
    session_id: str
    message_type: str  # "user", "agent_thinking", "agent_searching", "agent_response", "agent_courses"
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

class ChatSession(BaseModel):
    id: str
    user_id: Optional[str] = None
    created_at: datetime
    last_activity: datetime
    messages: List[ChatMessage] = []
    context: Dict[str, Any] = {}

class ChatStartRequest(BaseModel):
    user_id: Optional[str] = None

class ChatStartResponse(BaseModel):
    success: bool
    session_id: str
    message: str
    error: Optional[str] = None

class ChatMessageRequest(BaseModel):
    session_id: str
    message: str
    message_type: str = "user"

class ChatMessageResponse(BaseModel):
    success: bool
    message: ChatMessage
    session_id: str
    has_more_messages: bool = False
    error: Optional[str] = None

# Research Agent - Simplified version that avoids Pydantic conflicts
class SimpleResearchAgent:
    def __init__(self):
        self.initialized = False
        self.tools = []
        self.client = None
        self.graph = None
        
    async def initialize(self):
        """Initialize the research agent"""
        try:
            logger.info("🔄 Attempting to initialize research agent...")
            
            # Import here to avoid startup conflicts
            from langchain_core.messages import HumanMessage, SystemMessage
            from langchain.chat_models import init_chat_model
            from langgraph.graph import StateGraph, START, END, MessagesState
            from langgraph.prebuilt import ToolNode, tools_condition
            from langchain_mcp_adapters.client import MultiServerMCPClient
            
            # Get the absolute path to course_server.py
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            course_server_path = os.path.join(project_root, "course_server.py")
            
            logger.info(f"Looking for course_server.py at: {course_server_path}")
            
            if not os.path.exists(course_server_path):
                logger.warning(f"course_server.py not found at {course_server_path}")
                return False
            
            # Initialize MCP client
            self.client = MultiServerMCPClient({
                "course": {
                    "command": "python",
                    "args": [course_server_path],
                    "transport": "stdio",
                },
            })
            
            # Get tools from MCP server
            self.tools = await self.client.get_tools()
            logger.info(f"✅ Loaded {len(self.tools)} tools from MCP server")
            
            # Initialize the language model
            self.llm = init_chat_model("openai:gpt-4o")
            
            # Build the LangGraph
            self._build_graph(StateGraph, MessagesState, ToolNode, tools_condition, START, HumanMessage, SystemMessage)
            
            self.initialized = True
            logger.info("🚀 Research Agent initialized successfully!")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize Research Agent: {e}")
            logger.info("📝 Continuing with mock data...")
            return False
    
    def _build_graph(self, StateGraph, MessagesState, ToolNode, tools_condition, START, HumanMessage, SystemMessage):
        """Build the LangGraph"""
        system_message = """You are a helpful course research assistant. You have access to tools that can search for courses and extract detailed course information from DynamoDB.
        
        IMPORTANT: You MUST use the available tools to search for courses, then return ONLY the tool results in your response.
        
        Your workflow should be:
        1. First, use internal_vector_search_courses to find relevant courses
        2. If a specific course UUID is mentioned or requested, use get_course_details_by_uuid to get complete details
        3. If not enough courses found internally, use external_search_courses
        4. After calling the tools, respond with ONLY the course data returned by the tools
        
        CRITICAL: Your final response should contain the exact JSON structure returned by the tools. Do not add any commentary, explanation, or formatting. Just return the course data.
        """
        
        def chatbot(state):
            messages = state["messages"]
            if not any(hasattr(msg, 'type') and msg.type == "system" for msg in messages):
                messages = [SystemMessage(content=system_message)] + messages
            
            return {"messages": [self.llm.bind_tools(self.tools).invoke(messages)]}
        
        # Build the graph
        graph_builder = StateGraph(MessagesState)
        graph_builder.add_node("chatbot", chatbot)
        graph_builder.add_node("tools", ToolNode(self.tools))
        graph_builder.add_edge(START, "chatbot")
        graph_builder.add_conditional_edges("chatbot", tools_condition)
        graph_builder.add_edge("tools", "chatbot")
        
        self.graph = graph_builder.compile()
    
    async def search_courses(self, query: str, k: int = 10):
        """Search for courses"""
        if not self.initialized:
            # Return mock data if not initialized
            return self._get_mock_courses(query, k)
        
        try:
            # Import here to avoid conflicts
            from langchain_core.messages import HumanMessage
            
            user_input = f"Find me courses about {query}. I need about {k} courses. Please search both internal database and external sources if needed."
            
            logger.info(f"🔍 Research agent searching for: '{query}'")
            
            # Run the research agent
            conversation_state = {"messages": []}
            result = await self.graph.ainvoke({
                "messages": [HumanMessage(content=user_input)]
            })
            
            # Extract courses from actual tool results
            courses = self._extract_courses_from_tool_results(result, query, k)
            
            return {
                "success": True,
                "courses": courses,
                "total_results": len(courses),
                "query": query
            }
            
        except Exception as e:
            logger.error(f"❌ Error in research agent search: {e}")
            # Fallback to mock data
            return self._get_mock_courses(query, k)
    
    def _extract_courses_from_tool_results(self, result, query, k):
        """Extract courses from actual tool results"""
        courses = []
        
        logger.info(f"🔍 Extracting tool results for query: {query}")
        logger.info(f"📊 Result structure: {type(result)}")
        
        try:
            if result and "messages" in result:
                messages = result["messages"]
                logger.info(f"📝 Found {len(messages)} messages")
                
                # Look for tool call results in the messages
                for i, message in enumerate(messages):
                    logger.info(f"📧 Message {i}: type={type(message).__name__}")
                    
                    # Check for different message types and their content
                    if hasattr(message, 'tool_calls') and message.tool_calls:
                        logger.info(f"   🔧 Has {len(message.tool_calls)} tool calls")
                        for j, tool_call in enumerate(message.tool_calls):
                            logger.info(f"     Tool {j}: {tool_call.get('name', 'unknown')}")
                    
                    # Check for ToolMessage (actual tool results)
                    if hasattr(message, 'type') and message.type == 'tool':
                        logger.info(f"   🛠️ Tool result message found!")
                        logger.info(f"   Content: {str(message.content)[:200]}...")
                        
                        try:
                            import json
                            if isinstance(message.content, str):
                                tool_result = json.loads(message.content)
                            else:
                                tool_result = message.content
                                
                            logger.info(f"   🎯 Parsed tool result keys: {tool_result.keys() if isinstance(tool_result, dict) else type(tool_result)}")
                            
                            if isinstance(tool_result, dict):
                                if 'courses' in tool_result:
                                    logger.info(f"   📚 Found {len(tool_result['courses'])} courses")
                                    courses.extend(tool_result['courses'])
                                elif 'course' in tool_result and tool_result['course']:
                                    logger.info(f"   📖 Found single course")
                                    courses.append(tool_result['course'])
                        except (json.JSONDecodeError, Exception) as e:
                            logger.warning(f"   ❌ Error parsing tool result: {e}")
                    
                    # Also check content attribute directly
                    elif hasattr(message, 'content'):
                        if isinstance(message.content, list):
                            logger.info(f"   📄 Content blocks: {len(message.content)}")
                            for content_block in message.content:
                                if hasattr(content_block, 'type') and content_block.type == 'tool_result':
                                    logger.info(f"   🔍 Found tool_result block")
                                    try:
                                        import json
                                        tool_result = json.loads(content_block.content)
                                        if 'courses' in tool_result:
                                            courses.extend(tool_result['courses'])
                                        elif 'course' in tool_result and tool_result['course']:
                                            courses.append(tool_result['course'])
                                    except json.JSONDecodeError:
                                        continue
                        elif isinstance(message.content, str):
                            logger.info(f"   📄 String content: {message.content[:100]}...")
                
                # If we found courses from tools, use them
                if courses:
                    logger.info(f"✅ Successfully extracted {len(courses)} courses from tool results")
                    return courses[:k]  # Limit to requested number
                else:
                    logger.warning(f"⚠️ No courses found in tool results")
                    
        except Exception as e:
            logger.error(f"❌ Error extracting courses from tool results: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Fallback to mock data if no tool results found
        logger.info("📄 Trying simple extraction method...")
        courses = self._extract_courses_from_tool_results_simple(result, query, k)
        
        if courses:
            return courses
            
        logger.info("🎯 Trying final message extraction...")
        courses = self._extract_courses_from_final_message(result, query, k)
        
        if courses:
            return courses
            
        logger.info("📝 No tool results found with any method, using mock data")
        return self._get_mock_courses(query, k)["courses"]
    def _extract_courses_from_tool_results_simple(self, result, query, k):
        """Simplified extraction that looks for any course data in the conversation"""
        courses = []
        
        logger.info(f"🔍 Simple extraction for query: {query}")
        
        try:
            # Convert the entire result to string and look for course patterns
            result_str = str(result)
            logger.info(f"📄 Result string length: {len(result_str)}")
            
            # Look for JSON-like course data in the string
            import re
            import json
            
            # Pattern to find course data
            course_patterns = [
                r'"courses":\s*\[(.*?)\]',
                r"'courses':\s*\[(.*?)\]",
                r'courses.*?\[(.*?)\]'
            ]
            
            for pattern in course_patterns:
                matches = re.findall(pattern, result_str, re.DOTALL)
                for match in matches:
                    try:
                        # Try to parse the matched content
                        course_data = f'[{match}]'
                        parsed_courses = json.loads(course_data)
                        if isinstance(parsed_courses, list):
                            courses.extend(parsed_courses)
                            logger.info(f"✅ Found {len(parsed_courses)} courses using pattern matching")
                            break
                    except:
                        continue
            
            if courses:
                return courses[:k]
                
        except Exception as e:
            logger.error(f"❌ Error in simple extraction: {e}")
        
    def _extract_courses_from_final_message(self, result, query, k):
        """Extract courses from the final AI message content"""
        courses = []
        
        logger.info(f"🎯 Extracting from final message for query: {query}")
        
        try:
            if result and "messages" in result:
                messages = result["messages"]
                
                # Get the last message (should be the AI's final response)
                if messages:
                    last_message = messages[-1]
                    logger.info(f"🎤 Last message type: {type(last_message).__name__}")
                    
                    if hasattr(last_message, 'content'):
                        content = last_message.content
                        logger.info(f"💬 Content type: {type(content)}, length: {len(str(content))}")
                        
                        # Try to parse as JSON
                        import json
                        
                        if isinstance(content, str):
                            # Try to find JSON in the content
                            try:
                                # First try parsing the entire content
                                parsed = json.loads(content)
                                if isinstance(parsed, dict) and 'courses' in parsed:
                                    courses = parsed['courses']
                                    logger.info(f"✅ Found {len(courses)} courses in final message JSON")
                                elif isinstance(parsed, list):
                                    courses = parsed
                                    logger.info(f"✅ Found {len(courses)} courses in final message list")
                            except json.JSONDecodeError:
                                # Try to extract JSON from the content
                                import re
                                json_pattern = r'\{.*?"courses".*?\}'
                                matches = re.findall(json_pattern, content, re.DOTALL)
                                for match in matches:
                                    try:
                                        parsed = json.loads(match)
                                        if 'courses' in parsed:
                                            courses.extend(parsed['courses'])
                                            logger.info(f"✅ Found courses using regex extraction")
                                    except:
                                        continue
                
            return courses[:k] if courses else []
            
        except Exception as e:
            logger.error(f"❌ Error extracting from final message: {e}")
            return []
    
    def _get_mock_courses(self, query, k):
        """Fallback mock courses"""
        mock_courses = [
            {
                "uuid": f"mock-course-{i+1}",
                "title": f"{query.title()} Course {i+1}",
                "provider": "Mock University",
                "level": ["Beginner", "Intermediate", "Advanced"][i % 3],
                "skills": [query.title(), "Learning"],
                "description": f"A comprehensive course about {query}",
                "similarity_score": 0.8 - (i * 0.1)
            }
            for i in range(min(k, 3))
        ]
        
        return {
            "success": True,
            "courses": mock_courses,
            "total_results": len(mock_courses),
            "query": query
        }

# Global research agent instance
research_agent = SimpleResearchAgent()

# Chat Session Manager
class ChatSessionManager:
    def __init__(self):
        self.sessions: Dict[str, ChatSession] = {}
    
    def create_session(self, user_id: Optional[str] = None) -> ChatSession:
        """Create a new chat session"""
        session_id = str(uuid.uuid4())
        now = datetime.now()
        
        session = ChatSession(
            id=session_id,
            user_id=user_id,
            created_at=now,
            last_activity=now,
            messages=[],
            context={}
        )
        
        self.sessions[session_id] = session
        logger.info(f"💬 Created new chat session: {session_id}")
        return session
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get an existing session"""
        return self.sessions.get(session_id)
    
    def add_message(self, session_id: str, message_type: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[ChatMessage]:
        """Add a message to a session"""
        session = self.get_session(session_id)
        if not session:
            return None
        
        message_id = str(uuid.uuid4())
        now = datetime.now()
        
        message = ChatMessage(
            id=message_id,
            session_id=session_id,
            message_type=message_type,
            content=content,
            timestamp=now,
            metadata=metadata or {}
        )
        
        session.messages.append(message)
        session.last_activity = now
        
        logger.info(f"📝 Added {message_type} message to session {session_id}")
        return message
    
    def get_session_history(self, session_id: str) -> List[ChatMessage]:
        """Get all messages in a session"""
        session = self.get_session(session_id)
        return session.messages if session else []
    
    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Remove sessions older than max_age_hours"""
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        old_sessions = [sid for sid, session in self.sessions.items() 
                       if session.last_activity < cutoff]
        
        for session_id in old_sessions:
            del self.sessions[session_id]
            logger.info(f"🗑️ Cleaned up old session: {session_id}")

# Global session manager
session_manager = ChatSessionManager()

# Create FastAPI app
app = FastAPI(
    title="Grace Papers Backend API",
    description="AI Learning Platform Backend with Research Agent",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize research agent on startup"""
    logger.info("🚀 Starting Grace Papers Backend...")
    await research_agent.initialize()

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "Grace Papers Backend is running",
        "version": "1.0.0"
    }

# ===== CHAT ENDPOINTS =====

@app.post("/api/chat/start", response_model=ChatStartResponse)
async def start_chat_session(request: ChatStartRequest):
    """Start a new chat session"""
    try:
        session = session_manager.create_session(request.user_id)
        
        # Add initial welcome message
        welcome_message = session_manager.add_message(
            session.id, 
            "agent_response", 
            "Hello! I'm your course research assistant. I can help you find the best courses for your learning goals. What would you like to learn about?",
            {"is_welcome": True}
        )
        
        return ChatStartResponse(
            success=True,
            session_id=session.id,
            message="Chat session started successfully!"
        )
        
    except Exception as e:
        logger.error(f"❌ Error starting chat session: {e}")
        return ChatStartResponse(
            success=False,
            session_id="",
            message="Failed to start chat session",
            error=str(e)
        )

@app.get("/api/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """Get chat history for a session"""
    try:
        messages = session_manager.get_session_history(session_id)
        
        return {
            "success": True,
            "session_id": session_id,
            "messages": messages,
            "total_messages": len(messages)
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting chat history: {e}")
        return {
            "success": False,
            "session_id": session_id,
            "messages": [],
            "total_messages": 0,
            "error": str(e)
        }

# ===== END CHAT ENDPOINTS =====

@app.get("/api/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """Get chat history for a session"""
    try:
        messages = session_manager.get_session_history(session_id)
        
        return {
            "success": True,
            "session_id": session_id,
            "messages": messages,
            "total_messages": len(messages)
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting chat history: {e}")
        return {
            "success": False,
            "session_id": session_id,
            "messages": [],
            "total_messages": 0,
            "error": str(e)
        }

# ===== END CHAT ENDPOINTS =====

@app.post("/api/chat/message", response_model=ChatMessageResponse)
async def send_chat_message(request: ChatMessageRequest):
    """Send a message to the chat and get agent response"""
    try:
        # Verify session exists
        session = session_manager.get_session(request.session_id)
        if not session:
            return ChatMessageResponse(
                success=False,
                message=ChatMessage(
                    id="error",
                    session_id=request.session_id,
                    message_type="error",
                    content="Session not found",
                    timestamp=datetime.now()
                ),
                session_id=request.session_id,
                error="Session not found"
            )
        
        # Add user message to session
        user_message = session_manager.add_message(
            request.session_id,
            "user",
            request.message
        )
        
        if not user_message:
            return ChatMessageResponse(
                success=False,
                message=ChatMessage(
                    id="error",
                    session_id=request.session_id,
                    message_type="error",
                    content="Failed to save user message",
                    timestamp=datetime.now()
                ),
                session_id=request.session_id,
                error="Failed to save user message"
            )
        
        # For now, return the user message as confirmation
        # In Phase 2, we'll add the agent processing logic
        return ChatMessageResponse(
            success=True,
            message=user_message,
            session_id=request.session_id
        )
        
    except Exception as e:
        logger.error(f"❌ Error processing chat message: {e}")
        return ChatMessageResponse(
            success=False,
            message=ChatMessage(
                id="error",
                session_id=request.session_id,
                message_type="error",
                content="Failed to process message",
                timestamp=datetime.now()
            ),
            session_id=request.session_id,
            error=str(e)
        )

# Course search with research agent
@app.post("/api/search-courses", response_model=CourseSearchResponse)
async def search_courses(request: CourseSearchRequest):
    """Search for courses using the research agent"""
    logger.info(f"Course search request: query='{request.query}', k={request.k}")
    
    try:
        result = await research_agent.search_courses(request.query, request.k)
        
        courses = [
            Course(
                uuid=course["uuid"],
                title=course["title"],
                provider=course["provider"],
                level=course["level"],
                skills=course["skills"],
                description=course["description"],
                similarity_score=course["similarity_score"]
            )
            for course in result["courses"]
        ]
        
        return CourseSearchResponse(
            success=result["success"],
            courses=courses,
            total_results=result["total_results"],
            query=result["query"]
        )
        
    except Exception as e:
        logger.error(f"Error in search_courses: {e}")
        return CourseSearchResponse(
            success=False,
            courses=[],
            total_results=0,
            query=request.query,
            error=str(e)
        )

# Other endpoints (same as before)
@app.post("/api/save-study-plan", response_model=StudyPlanResponse)
async def save_study_plan(request: StudyPlanRequest):
    logger.info(f"Saving study plan for user {request.userId} with {len(request.courses)} courses")
    return StudyPlanResponse(
        success=True,
        message=f"Study plan saved successfully for user {request.userId}",
        courses_count=len(request.courses)
    )

@app.get("/api/user-profile/{user_id}")
async def get_user_profile(user_id: str):
    return {
        "success": True,
        "profile": {
            "id": user_id,
            "name": "Sarah Chen",
            "role": "Marketing Manager",
            "experience": "Beginner",
            "goals": ["AI Tools Proficiency", "Data Analysis", "Automation"],
            "completedCourses": 3,
            "totalHours": 24
        }
    }

@app.get("/api/study-plan/{user_id}")
async def get_study_plan(user_id: str):
    return {
        "success": True,
        "study_plan": [],
        "user_id": user_id
    }

@app.get("/api/courses/health")
async def courses_health_check():
    """Health check for the course service and research agent"""
    return {
        "status": "healthy",
        "research_agent_initialized": research_agent.initialized,
        "tools_loaded": len(research_agent.tools) if research_agent.tools else 0
    }

@app.get("/api/debug/tools")
async def debug_available_tools():
    """Debug endpoint to see what tools are available"""
    if not research_agent.initialized:
        return {
            "success": False,
            "error": "Research agent not initialized",
            "tools": []
        }
    
    try:
        # Get tool information
        tool_info = []
        for tool in research_agent.tools:
            tool_info.append({
                "name": tool.name,
                "description": tool.description,
                "args": tool.args if hasattr(tool, 'args') else str(tool.args_schema) if hasattr(tool, 'args_schema') else "N/A"
            })
        
        return {
            "success": True,
            "total_tools": len(research_agent.tools),
            "tools": tool_info
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "tools": []
        }

@app.post("/api/agent-search-courses")
async def agent_search_courses_direct(request: CourseSearchRequest):
    """Direct agent search that returns raw tool results without parsing"""
    logger.info(f"Agent direct search: query='{request.query}', k={request.k}")
    
    if not research_agent.initialized:
        return {
            "success": False,
            "error": "Research agent not initialized",
            "courses": []
        }
    
    try:
        from langchain_core.messages import HumanMessage
        
        user_input = f"Find me courses about {request.query}. I need about {request.k} courses. Use internal_vector_search_courses first, then external_search_courses if needed."
        
        logger.info(f"🔍 Agent direct search for: '{request.query}'")
        
        # Run the research agent
        result = await research_agent.graph.ainvoke({
            "messages": [HumanMessage(content=user_input)]
        })
        
        # Return the raw tool results directly
        # Extract course data from tool results
        courses = research_agent._extract_courses_from_tool_results(result, request.query, request.k)
        
        # Return the structured course data
        return {
            "success": True,
            "query": request.query,
            "courses": courses,
            "total_results": len(courses),
            "message": "Agent completed search successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Error in agent direct search: {e}")
        return {
            "success": False,
            "error": str(e),
            "query": request.query
        }

@app.get("/api/course/{course_id}")
async def get_course_details(course_id: str):
    return {
        "success": True,
        "course": {
            "uuid": course_id,
            "title": f"Course Details for {course_id}",
            "description": "Detailed course information",
            "provider": "Research Provider",
            "level": "Beginner",
            "skills": ["Course Skills"],
            "duration": "4 weeks",
            "rating": 4.5,
            "url": f"https://example.com/course/{course_id}"
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    
    logger.info(f"🚀 Starting Grace Papers Backend on port {port}")
    
    uvicorn.run(
        "main_with_agent:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
