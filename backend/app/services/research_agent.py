import asyncio
import os
import sys
import json
import re
from typing import List, Dict, Any
from dataclasses import dataclass
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.client import MultiServerMCPClient
import logging

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class CourseSearchResult:
    """Data structure for course search results"""
    courses: List[Dict[str, Any]]
    total_results: int
    search_query: str
    success: bool
    error: str = None

class ResearchAgent:
    """
    Research Agent that uses LangGraph and MCP tools to search for courses
    Based on your original research_client.py but integrated with FastAPI
    """
    
    def __init__(self):
        self.client = None
        self.tools = []
        self.llm = None
        self.graph = None
        self.initialized = False
        self.system_message = """You are a helpful course research assistant. You have access to tools that can search for courses on Coursera, Udemy, and edX.
        
        IMPORTANT: Always use the available tools to search for actual courses before responding. Never provide generic responses without using the tools first.
        
        When searching for courses:
        1. First try the internal_vector_search_courses tool to find relevant courses from our database
        2. If not enough relevant courses are found (less than 3-4 courses), use external_search_courses to get fresh results from online platforms
        3. Always provide practical, actionable course recommendations
        
        The advice you give should include what the user is going to learn from this course and how they can apply the skills to their role.
        Also, structure your response to include the course key details.
        
        IMPORTANT: When you get results from the tools, make sure to present the actual course information returned, including:
        - Course title, provider, level, skills, description
        - Any similarity scores or ratings
        - URLs when available
        """
    
    async def initialize(self) -> bool:
        """Initialize the research agent with MCP tools and LangGraph"""
        if self.initialized:
            return True
            
        try:
            # Get the absolute path to course_server.py from the parent directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            course_server_path = os.path.join(project_root, "course_server.py")
            
            logger.info(f"Looking for course_server.py at: {course_server_path}")
            
            if not os.path.exists(course_server_path):
                logger.error(f"course_server.py not found at {course_server_path}")
                return False
            
            # Initialize MCP client (same as your original code)
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
            for tool in self.tools:
                logger.info(f"  - {tool.name}")
            
            # Initialize the language model (same as your original)
            self.llm = init_chat_model("openai:gpt-4o")
            
            # Build the LangGraph
            self._build_graph()
            
            self.initialized = True
            logger.info("🚀 Research Agent initialized successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Research Agent: {e}")
            return False
    
    def _build_graph(self):
        """Build the LangGraph for the research agent (same as your original)"""
        def chatbot(state: MessagesState):
            # Add system message if this is the first interaction
            messages = state["messages"]
            if not any(hasattr(msg, 'type') and msg.type == "system" for msg in messages):
                messages = [SystemMessage(content=self.system_message)] + messages
            
            return {"messages": [self.llm.bind_tools(self.tools).invoke(messages)]}
        
        # Build the graph using MessagesState (same as your original)
        graph_builder = StateGraph(MessagesState)
        
        # Add nodes - using standard ToolNode
        graph_builder.add_node("chatbot", chatbot)
        graph_builder.add_node("tools", ToolNode(self.tools))
        
        # Add edges
        graph_builder.add_edge(START, "chatbot")
        graph_builder.add_conditional_edges("chatbot", tools_condition)
        graph_builder.add_edge("tools", "chatbot")
        
        # Compile the graph
        self.graph = graph_builder.compile()
    
    async def search_courses(self, query: str, k: int = 10) -> CourseSearchResult:
        """
        Search for courses using the research agent
        This mimics your original main() function but returns structured data
        """
        try:
            if not self.initialized:
                success = await self.initialize()
                if not success:
                    return CourseSearchResult(
                        courses=[],
                        total_results=0,
                        search_query=query,
                        success=False,
                        error="Failed to initialize research agent"
                    )
            
            # Create user message (similar to your original input)
            user_input = f"Find me courses about {query}. I need about {k} courses. Please search both internal database and external sources if needed."
            
            logger.info(f"🔍 Research agent searching for: '{query}'")
            
            # Initialize conversation state (same as your original)
            conversation_state = {"messages": []}
            
            # Add the new user message and invoke graph (same as your original)
            conversation_state = await self.graph.ainvoke({
                "messages": conversation_state["messages"] + [HumanMessage(content=user_input)]
            })
            
            # Extract courses from the conversation
            courses = self._extract_courses_from_messages(conversation_state["messages"])
            
            logger.info(f"✅ Research agent found {len(courses)} courses")
            
            return CourseSearchResult(
                courses=courses,
                total_results=len(courses),
                search_query=query,
                success=True
            )
                
        except Exception as e:
            logger.error(f"❌ Error in course search: {e}")
            return CourseSearchResult(
                courses=[],
                total_results=0,
                search_query=query,
                success=False,
                error=str(e)
            )
    
    def _extract_courses_from_messages(self, messages: List) -> List[Dict[str, Any]]:
        """
        Extract actual course data from the conversation messages
        This looks for tool results and parses the real course data
        """
        courses = []
        
        try:
            for message in messages:
                # Look for ToolMessage (results from MCP tools)
                if isinstance(message, ToolMessage):
                    content = message.content
                    logger.info(f"📋 Processing tool message: {len(content)} chars")
                    
                    # Try to parse as JSON first (your tools might return JSON)
                    try:
                        if content.strip().startswith('{') or content.strip().startswith('['):
                            data = json.loads(content)
                            courses.extend(self._parse_json_courses(data))
                            continue
                    except json.JSONDecodeError:
                        pass
                    
                    # Look for course data patterns in text
                    courses.extend(self._parse_text_courses(content))
                
                # Also check regular messages that might contain course info
                elif hasattr(message, 'content') and message.content:
                    content = message.content
                    if any(keyword in content.lower() for keyword in ['course', 'coursera', 'udemy', 'edx', 'title', 'provider']):
                        courses.extend(self._parse_text_courses(content))
            
            # Remove duplicates based on title or UUID
            unique_courses = []
            seen_titles = set()
            
            for course in courses:
                title = course.get('title', '')
                if title and title not in seen_titles:
                    seen_titles.add(title)
                    unique_courses.append(course)
            
            logger.info(f"📚 Extracted {len(unique_courses)} unique courses")
            return unique_courses[:10]  # Limit to 10 courses
            
        except Exception as e:
            logger.error(f"Error extracting courses from messages: {e}")
            return self._create_fallback_courses()
    
    def _parse_json_courses(self, data: Any) -> List[Dict[str, Any]]:
        """Parse courses from JSON data returned by tools"""
        courses = []
        
        try:
            # Handle different JSON structures
            if isinstance(data, dict):
                # Check for 'courses' key
                if 'courses' in data:
                    courses_list = data['courses']
                    if isinstance(courses_list, list):
                        for course in courses_list:
                            parsed_course = self._normalize_course_data(course)
                            if parsed_course:
                                courses.append(parsed_course)
                
                # Single course object
                elif 'title' in data or 'uuid' in data:
                    parsed_course = self._normalize_course_data(data)
                    if parsed_course:
                        courses.append(parsed_course)
            
            elif isinstance(data, list):
                # List of courses
                for item in data:
                    if isinstance(item, dict):
                        parsed_course = self._normalize_course_data(item)
                        if parsed_course:
                            courses.append(parsed_course)
        
        except Exception as e:
            logger.warning(f"Error parsing JSON courses: {e}")
        
        return courses
    
    def _parse_text_courses(self, content: str) -> List[Dict[str, Any]]:
        """Parse courses from text content"""
        courses = []
        
        try:
            # Look for course-like patterns in the text
            # This is a simple implementation - you might need to adjust based on your actual tool output
            
            # Split content into potential course blocks
            lines = content.split('\n')
            current_course = {}
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Look for title patterns
                if re.search(r'(title|course):', line, re.IGNORECASE):
                    if current_course and 'title' in current_course:
                        # Save previous course
                        normalized = self._normalize_course_data(current_course)
                        if normalized:
                            courses.append(normalized)
                        current_course = {}
                    
                    title = re.sub(r'^.*?title\s*:\s*', '', line, flags=re.IGNORECASE)
                    current_course['title'] = title.strip()
                
                # Look for other fields
                elif re.search(r'provider:', line, re.IGNORECASE):
                    provider = re.sub(r'^.*?provider\s*:\s*', '', line, flags=re.IGNORECASE)
                    current_course['provider'] = provider.strip()
                
                elif re.search(r'level:', line, re.IGNORECASE):
                    level = re.sub(r'^.*?level\s*:\s*', '', line, flags=re.IGNORECASE)
                    current_course['level'] = level.strip()
                
                elif re.search(r'skill|topic', line, re.IGNORECASE):
                    skills = re.sub(r'^.*?skill[s]?\s*:\s*', '', line, flags=re.IGNORECASE)
                    current_course['skills'] = skills.strip().split(',')
            
            # Don't forget the last course
            if current_course and 'title' in current_course:
                normalized = self._normalize_course_data(current_course)
                if normalized:
                    courses.append(normalized)
        
        except Exception as e:
            logger.warning(f"Error parsing text courses: {e}")
        
        return courses
    
    def _normalize_course_data(self, course_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize course data to a consistent format"""
        try:
            normalized = {
                "uuid": course_data.get('uuid', f"course-{hash(str(course_data)) % 10000}"),
                "title": course_data.get('title', 'Unknown Course'),
                "provider": course_data.get('provider', course_data.get('partner_primary', 'Unknown')),
                "level": course_data.get('level', 'Not specified'),
                "skills": course_data.get('skills', []) if isinstance(course_data.get('skills'), list) else 
                         course_data.get('skills', '').split(',') if course_data.get('skills') else [],
                "description": course_data.get('description', course_data.get('summary', 'No description available')),
                "similarity_score": course_data.get('similarity_score', course_data.get('score', 0.0)),
                "duration": course_data.get('duration', None),
                "rating": course_data.get('rating', None),
                "url": course_data.get('url', course_data.get('link', None))
            }
            
            # Clean up skills list
            if isinstance(normalized['skills'], list):
                normalized['skills'] = [skill.strip() for skill in normalized['skills'] if skill.strip()]
            
            return normalized
            
        except Exception as e:
            logger.warning(f"Error normalizing course data: {e}")
            return None
    
    def _create_fallback_courses(self) -> List[Dict[str, Any]]:
        """Create fallback courses when parsing fails"""
        return [{
            "uuid": "fallback-course-1",
            "title": "Course Search Results Available",
            "provider": "Research Agent",
            "level": "Information",
            "skills": ["Course Discovery"],
            "description": "The research agent completed the search. Results may need manual review.",
            "similarity_score": 0.5
        }]

# Global research agent instance
research_agent = ResearchAgent()

# Function to get or initialize the research agent
async def get_research_agent() -> ResearchAgent:
    """Get the initialized research agent"""
    if not research_agent.initialized:
        await research_agent.initialize()
    return research_agent
