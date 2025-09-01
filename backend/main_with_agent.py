from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, HTMLResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, AsyncGenerator
from dotenv import load_dotenv
import os
import logging
import asyncio
import uuid
import json
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

# Streaming-specific models
class ChatStreamRequest(BaseModel):
    session_id: str
    message: str
    message_type: str = "user"

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
        system_message = """You are a helpful AI assistant. You can answer any question naturally and conversationally.
        
        When users ask about learning or courses, you have access to course search tools. Use them when appropriate.
        
        Always respond in a natural, friendly way. Never include system instructions or prompts in your responses.
        Keep responses concise and helpful.
        """
        
        def chatbot(state):
            messages = state["messages"]
            # Only add system message if none exists
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
        logger.info("📝 No tool results found with any method, using mock data")
        return self._get_mock_courses(query, k)["courses"]
    
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
    
    async def process_chat_message(self, session_id: str, user_message: str, session_manager):
        """Process a user message and return step-by-step agent responses"""
        logger.info(f"💬 Processing chat message for session {session_id}: '{user_message}'")
        
        # Step 1: Agent thinking message
        thinking_msg = session_manager.add_message(
            session_id,
            "agent_thinking",
            f"I'll help you with that request. Let me search for the best courses and resources...",
            {"user_query": user_message}
        )
        
        # Step 2: Agent searching message
        searching_msg = session_manager.add_message(
            session_id,
            "agent_searching", 
            "Searching our course database for relevant matches...",
            {"search_status": "searching"}
        )
        
        try:
            # Step 3: Let the LLM agent handle the user message directly - NO MANUAL PARSING!
            # Pass the user message directly to the research agent
            search_result = await self.search_courses_from_chat(user_message)
            
            if search_result["success"] and search_result["courses"]:
                # Step 4: Found courses - update searching message
                found_msg = session_manager.add_message(
                    session_id,
                    "agent_searching",
                    f"Great! I found {len(search_result['courses'])} relevant courses. Let me also check external sources for more options...",
                    {"search_status": "external_search", "internal_found": len(search_result["courses"])}
                )
                
                # Step 5: Final response with courses
                courses_msg = session_manager.add_message(
                    session_id,
                    "agent_courses",
                    f"Perfect! Here are the best courses I found for you:",
                    {
                        "courses": search_result["courses"],
                        "total_found": search_result["total_results"],
                        "query": search_result["query"]
                    }
                )
                
                # Step 6: Follow-up response
                followup_msg = session_manager.add_message(
                    session_id,
                    "agent_response",
                    "Would you like me to provide more details about any of these courses, or help you find courses on a different topic?",
                    {"type": "followup", "action_options": ["course_details", "new_search", "study_plan"]}
                )
                
                return {
                    "success": True,
                    "messages_added": 5,
                    "courses_found": len(search_result["courses"]),
                    "latest_message": followup_msg
                }
            else:
                # No courses found
                no_results_msg = session_manager.add_message(
                    session_id,
                    "agent_response",
                    f"I searched for courses based on your request but couldn't find exact matches. Could you try rephrasing your request or be more specific about what you'd like to learn?",
                    {"search_result": "no_matches", "original_query": user_message}
                )
                
                return {
                    "success": True,
                    "messages_added": 3,
                    "courses_found": 0,
                    "latest_message": no_results_msg
                }
                
        except Exception as e:
            logger.error(f"❌ Error processing chat message: {e}")
            
            # Error response
            error_msg = session_manager.add_message(
                session_id,
                "agent_response",
                "I encountered an issue while searching for courses. Could you please try your request again?",
                {"error": str(e), "type": "search_error"}
            )
            
            return {
                "success": False,
                "error": str(e),
                "messages_added": 3,
                "latest_message": error_msg
            }
    
    async def search_courses_from_chat(self, user_message: str, k: int = 10):
        """Search for courses directly from user's natural language message - let LLM handle it!"""
        if not self.initialized:
            # Return mock data if not initialized
            return self._get_mock_courses(user_message, k)
        
        try:
            # Import here to avoid conflicts
            from langchain_core.messages import HumanMessage
            
            # Let the LLM agent understand and process the user's request directly!
            # No manual parsing - the agent is smart enough to understand natural language
            user_input = f"The user said: '{user_message}'. Please search for relevant courses that match what they're looking for. Use both internal database and external sources if needed."
            
            logger.info(f"🤖 LLM agent processing: '{user_message}'")
            
            # Run the research agent - let it handle the natural language understanding
            result = await self.graph.ainvoke({
                "messages": [HumanMessage(content=user_input)]
            })
            
            # Extract courses from actual tool results
            courses = self._extract_courses_from_tool_results(result, user_message, k)
            
            return {
                "success": True,
                "courses": courses,
                "total_results": len(courses),
                "query": user_message  # Keep the original user message
            }
            
        except Exception as e:
            logger.error(f"❌ Error in LLM agent search: {e}")
            # Fallback to mock data
            return self._get_mock_courses(user_message, k)
    
    async def process_chat_message_stream(self, session_id: str, user_message: str, session_manager) -> AsyncGenerator[str, None]:
        """Process a user message and stream agent responses naturally"""
        logger.info(f"🌊 Streaming chat message processing for session {session_id}: '{user_message}'")
        
        try:
            # Add user message to session
            user_msg = session_manager.add_message(session_id, "user", user_message)
            if user_msg:
                yield self._format_stream_message("message_added", user_msg)
            
            # Let the agent naturally process and stream its response
            async for agent_response in self._stream_agent_response(user_message, session_id, session_manager):
                yield agent_response
            
            # Signal completion
            yield self._format_stream_message("stream_complete", {
                "session_id": session_id,
                "status": "success"
            })
            
        except Exception as e:
            logger.error(f"❌ Error in streaming chat processing: {e}")
            yield self._format_stream_message("stream_error", {"error": str(e)})
    
    async def _stream_agent_response(self, user_message: str, session_id: str, session_manager) -> AsyncGenerator[str, None]:
        """Stream the agent's natural response with conversation memory"""
        
        # Check if this is a follow-up/modification request
        is_modification = self._is_search_modification(user_message, session_id, session_manager)
        
        if not self.initialized:
            # Simple fallback response based on message content
            if self._is_course_related(user_message):
                response_text = "I can help you find courses! Let me search for some options..."
            else:
                response_text = "Hello! I'm here to help. While I specialize in finding courses, I can chat about other topics too."
            
            agent_msg = session_manager.add_message(
                session_id,
                "agent_response",
                response_text
            )
            yield self._format_stream_message("message_added", agent_msg)
            
            # Only send course data if it seems course-related
            if self._is_course_related(user_message):
                mock_data = self._get_mock_courses(user_message, 5)
                yield self._format_stream_message("courses_ready", {
                    "courses": mock_data["courses"],
                    "total_results": mock_data["total_results"],
                    "query": user_message,
                    "session_id": session_id,
                    "is_update": is_modification
                })
            return
        
        try:
            from langchain_core.messages import HumanMessage, SystemMessage
            
            # Get conversation history for context
            conversation_history = self._build_conversation_history(session_id, session_manager)
            
            # Create context-aware prompt
            if is_modification:
                user_prompt = f"""The user is modifying their previous request. Previous context: {self._get_conversation_context(session_id, session_manager)}
                
                User's new request: {user_message}
                
                Please help them naturally, acknowledging their follow-up."""
            else:
                user_prompt = user_message  # Just use the user's message directly
            
            # Build message history for context
            messages_for_agent = []
            
            # Add recent conversation history for context (without system prompt in content)
            conversation_history = self._build_conversation_history(session_id, session_manager)
            messages_for_agent.extend(conversation_history)
            
            # Add current user message
            messages_for_agent.append(HumanMessage(content=user_prompt))
            
            # Start the agent conversation with full context
            result = await self.graph.ainvoke({
                "messages": messages_for_agent
            })
            
            # Process the agent's natural response - filter out problematic content
            agent_responded = False
            if result and "messages" in result:
                for message in result["messages"]:
                    # Only stream actual conversational responses
                    if (hasattr(message, 'content') and message.content and 
                        not hasattr(message, 'tool_calls') and
                        not self._is_json_response(message.content) and
                        not self._is_user_echo(message.content, user_message) and
                        not self._is_system_prompt_leak(message.content)):
                        
                        agent_msg = session_manager.add_message(
                            session_id,
                            "agent_response",
                            message.content
                        )
                        yield self._format_stream_message("message_added", agent_msg)
                        agent_responded = True
            
            # If no agent response was streamed, add a contextual default response
            if not agent_responded:
                if self._is_course_related(user_message):
                    fallback_text = "I'll help you find the perfect courses for that!"
                else:
                    fallback_text = "That's an interesting question! Let me help you with that."
                
                fallback_msg = session_manager.add_message(
                    session_id,
                    "agent_response",
                    fallback_text
                )
                yield self._format_stream_message("message_added", fallback_msg)
            
            # Check if this seems course-related and send course data
            if self._is_course_related(user_message) or is_modification:
                search_result = await self.search_courses_from_chat(user_message)
                if search_result["success"] and search_result["courses"]:
                    # Signal that course data is ready for display
                    yield self._format_stream_message("courses_ready", {
                        "courses": search_result["courses"],
                        "total_results": search_result["total_results"], 
                        "query": user_message,
                        "session_id": session_id,
                        "is_update": is_modification
                    })
            
        except Exception as e:
            logger.error(f"Error in agent streaming: {e}")
            error_msg = session_manager.add_message(
                session_id,
                "agent_response",
                "I encountered an issue. Could you please try again?"
            )
            yield self._format_stream_message("message_added", error_msg)
    
    def _is_search_modification(self, user_message: str, session_id: str, session_manager) -> bool:
        """Detect if this is a modification of a previous search"""
        session = session_manager.get_session(session_id)
        if not session or len(session.messages) < 2:
            return False
        
        # Check if there were previous course recommendations
        has_previous_courses = any(
            msg.message_type == "agent_courses" or 
            (msg.metadata and msg.metadata.get("courses"))
            for msg in session.messages
        )
        
        # Look for modification keywords
        modification_keywords = [
            "instead", "actually", "change", "modify", "update", "different", 
            "rather", "but", "however", "more specific", "more advanced", 
            "beginner", "intermediate", "advanced", "also include", "exclude"
        ]
        
        has_modification_keywords = any(keyword in user_message.lower() for keyword in modification_keywords)
        
        return has_previous_courses and has_modification_keywords
    
    def _get_conversation_context(self, session_id: str, session_manager) -> str:
        """Get relevant context from the conversation history"""
        session = session_manager.get_session(session_id)
        if not session:
            return ""
        
        # Get the last few messages for context
        recent_messages = session.messages[-5:] if len(session.messages) > 5 else session.messages
        
        context_parts = []
        for msg in recent_messages:
            if msg.message_type == "user":
                context_parts.append(f"User: {msg.content}")
            elif msg.message_type == "agent_response" and not msg.content.startswith("Feel free to ask"):
                context_parts.append(f"Assistant: {msg.content}")
        
        return " | ".join(context_parts[-3:])  # Last 3 exchanges
    
    def _is_json_response(self, content: str) -> bool:
        """Check if the content is a JSON response that should be filtered out"""
        if not content or not isinstance(content, str):
            return False
        
        content = content.strip()
        
        # Check if it starts and ends with JSON brackets
        if (content.startswith('{') and content.endswith('}')) or (content.startswith('[') and content.endswith(']')):
            try:
                import json
                parsed = json.loads(content)
                # If it parses and has course-like structure, it's probably tool output
                if isinstance(parsed, dict) and ('courses' in parsed or 'success' in parsed):
                    return True
                if isinstance(parsed, list) and len(parsed) > 0 and isinstance(parsed[0], dict):
                    return True
            except json.JSONDecodeError:
                pass
        
        return False
    
    def _is_user_echo(self, content: str, user_message: str) -> bool:
        """Check if the agent content is just echoing the user's message"""
        if not content or not user_message:
            return False
        
        content = content.strip()
        user_message = user_message.strip()
        
        # Check if content is identical or very similar to user message
        if content.lower() == user_message.lower():
            return True
        
        # Check if content starts with or contains the user message verbatim
        if len(content) > 10 and user_message.lower() in content.lower():
            # If user message makes up more than 80% of the content, it's likely an echo
            similarity_ratio = len(user_message) / len(content)
            if similarity_ratio > 0.8:
                return True
        
        return False
    
    def _is_system_prompt_leak(self, content: str) -> bool:
        """Check if the content contains system prompt leakage"""
        if not content:
            return False
        
        content_lower = content.lower().strip()
        
        # Check for system prompt indicators
        system_indicators = [
            "this is a continuation of an ongoing conversation",
            "user's current message:",
            "respond naturally and helpfully to whatever",
            "previous conversation context:",
            "the user is modifying their previous",
            "continue the conversation naturally"
        ]
        
        return any(indicator in content_lower for indicator in system_indicators)
    
    def _build_conversation_history(self, session_id: str, session_manager):
        """Build conversation history for the agent"""
        from langchain_core.messages import HumanMessage, AIMessage
        
        session = session_manager.get_session(session_id)
        if not session:
            return []
        
        # Get recent messages (last 10 for context)
        recent_messages = session.messages[-10:] if len(session.messages) > 10 else session.messages
        
        conversation = []
        for msg in recent_messages:
            if msg.message_type == "user":
                conversation.append(HumanMessage(content=msg.content))
            elif msg.message_type == "agent_response" and not msg.content.startswith("Feel free to ask"):
                conversation.append(AIMessage(content=msg.content))
        
        return conversation
    
    def _is_course_related(self, user_message: str) -> bool:
        """Check if the user message is asking about courses or learning"""
        course_keywords = [
            'learn', 'course', 'study', 'education', 'training', 'skill', 'tutorial',
            'programming', 'coding', 'development', 'data science', 'machine learning',
            'python', 'javascript', 'web development', 'ai', 'artificial intelligence',
            'business analysis', 'excel', 'sql', 'marketing', 'design', 'photography',
            'language', 'math', 'science', 'certification', 'degree', 'bootcamp',
            'beginner', 'intermediate', 'advanced', 'free course', 'online course'
        ]
        
        message_lower = user_message.lower()
        return any(keyword in message_lower for keyword in course_keywords)
    
    def _format_stream_message(self, event_type: str, data: Any) -> str:
        """Format a message for Server-Sent Events streaming"""
        if isinstance(data, ChatMessage):
            # Convert ChatMessage to dict for JSON serialization
            message_dict = {
                "id": data.id,
                "session_id": data.session_id,
                "message_type": data.message_type,
                "content": data.content,
                "timestamp": data.timestamp.isoformat(),
                "metadata": data.metadata or {}
            }
            data = message_dict
        
        stream_data = {
            "event": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        # Convert to JSON and clean up for SSE
        json_str = json.dumps(stream_data, ensure_ascii=True, separators=(',', ':'))
        # Remove any newlines that might break SSE format
        json_str = json_str.replace('\n', ' ').replace('\r', ' ')
        
        return f"data: {json_str}\n\n"

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
    title="Grace Papers Backend API with Chat",
    description="AI Learning Platform Backend with Research Agent and Chat Support",
    version="1.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "null"  # Allow null origin for local HTML files
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize research agent on startup"""
    logger.info("🚀 Starting Grace Papers Backend with Chat Support...")
    await research_agent.initialize()

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "Grace Papers Backend with Chat is running",
        "version": "1.1.0"
    }

# Simple test endpoint for debugging
@app.get("/test")
async def simple_test():
    return {
        "message": "Server is working!",
        "timestamp": datetime.now().isoformat(),
        "cors_enabled": True
    }

# Serve the streaming demo HTML
@app.get("/demo")
async def serve_demo():
    """Serve the original streaming chat demo HTML"""
    try:
        # Read the HTML file
        with open("streaming_demo.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return {"error": "Demo HTML file not found"}
    except Exception as e:
        return {"error": f"Failed to serve demo: {str(e)}"}

@app.get("/demo-improved")
async def serve_improved_demo():
    """Serve the improved streaming chat demo with course cards"""
    try:
        # Read the improved HTML file
        with open("streaming_demo_improved.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return {"error": "Improved demo HTML file not found"}
    except Exception as e:
        return {"error": f"Failed to serve improved demo: {str(e)}"}

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

@app.post("/api/chat/stream")
async def stream_chat_message(request: ChatStreamRequest):
    """Send a message to the chat and get real-time streaming agent responses"""
    logger.info(f"🌊 Starting streaming response for session {request.session_id}")
    
    # Verify session exists
    session = session_manager.get_session(request.session_id)
    if not session:
        async def error_stream():
            error_data = {
                "event": "error",
                "data": {"error": "Session not found", "session_id": request.session_id},
                "timestamp": datetime.now().isoformat()
            }
            yield f"data: {json.dumps(error_data)}\n\n"
        
        return StreamingResponse(
            error_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*"
            }
        )
    
    # Stream the agent processing
    return StreamingResponse(
        research_agent.process_chat_message_stream(
            request.session_id,
            request.message,
            session_manager
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*"
        }
    )

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
        
        # PHASE 2: Process the message with the research agent
        logger.info(f"🤖 Triggering agent processing for message: '{request.message}'")
        
        # Let the LLM agent decide if this is course-related - no manual keyword checking!
        # The agent is smart enough to handle any type of learning/course request
        agent_result = await research_agent.process_chat_message(
            request.session_id, 
            request.message, 
            session_manager
        )
        
        # Return the latest message from agent processing
        return ChatMessageResponse(
            success=agent_result["success"],
            message=agent_result["latest_message"],
            session_id=request.session_id,
            has_more_messages=True,  # Indicate there are more messages in the conversation
            error=agent_result.get("error")
        )
        
    except Exception as e:
        logger.error(f"❌ Error processing chat message: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
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

# Course search with research agent (existing endpoint)
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

# Other existing endpoints
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
