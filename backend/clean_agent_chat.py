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
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Models
class ChatMessage(BaseModel):
    id: str
    session_id: str
    message_type: str  # "user" or "assistant"
    content: str
    timestamp: datetime

class ChatSession(BaseModel):
    id: str
    messages: List[ChatMessage] = []
    created_at: datetime
    last_activity: datetime

class ChatRequest(BaseModel):
    session_id: str
    message: str

# Clean Agent Implementation
class CleanChatAgent:
    def __init__(self):
        self.initialized = False
        self.sessions: Dict[str, ChatSession] = {}
        self.client = None
        self.graph = None
        self.tools = []
        
    async def initialize(self):
        """Initialize the LangGraph agent"""
        try:
            logger.info("🔄 Initializing clean chat agent...")
            
            # Import LangGraph components
            from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
            from langchain.chat_models import init_chat_model
            from langgraph.graph import StateGraph, START, MessagesState
            from langgraph.prebuilt import ToolNode, tools_condition
            from langchain_mcp_adapters.client import MultiServerMCPClient
            
            # Get course server path
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            course_server_path = os.path.join(project_root, "course_server.py")
            
            if not os.path.exists(course_server_path):
                logger.error(f"course_server.py not found at {course_server_path}")
                return False
            
            # Initialize MCP client
            self.client = MultiServerMCPClient({
                "course": {
                    "command": "python",
                    "args": [course_server_path],
                    "transport": "stdio",
                },
            })
            
            # Get tools
            self.tools = await self.client.get_tools()
            logger.info(f"✅ Loaded {len(self.tools)} tools: {[tool.name for tool in self.tools]}")
            
            # Initialize LLM
            self.llm = init_chat_model("openai:gpt-4o")
            
            # Build simple graph
            self._build_graph(StateGraph, MessagesState, ToolNode, tools_condition, START)
            
            self.initialized = True
            logger.info("🚀 Clean chat agent initialized!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize agent: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _build_graph(self, StateGraph, MessagesState, ToolNode, tools_condition, START):
        """Build simple LangGraph"""
        
        def chatbot(state):
            """Simple chatbot node"""
            return {"messages": [self.llm.bind_tools(self.tools).invoke(state["messages"])]}
        
        # Build graph
        graph_builder = StateGraph(MessagesState)
        graph_builder.add_node("chatbot", chatbot)
        graph_builder.add_node("tools", ToolNode(self.tools))
        graph_builder.add_edge(START, "chatbot")
        graph_builder.add_conditional_edges("chatbot", tools_condition)
        graph_builder.add_edge("tools", "chatbot")
        
        self.graph = graph_builder.compile()
    
    def create_session(self) -> str:
        """Create new chat session"""
        session_id = str(uuid.uuid4())
        session = ChatSession(
            id=session_id,
            created_at=datetime.now(),
            last_activity=datetime.now()
        )
        self.sessions[session_id] = session
        logger.info(f"💬 Created session: {session_id}")
        return session_id
    
    def add_message(self, session_id: str, message_type: str, content: str) -> Optional[ChatMessage]:
        """Add message to session"""
        session = self.sessions.get(session_id)
        if not session:
            logger.warning(f"Session not found: {session_id}")
            return None
            
        message = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=session_id,
            message_type=message_type,
            content=content,
            timestamp=datetime.now()
        )
        
        session.messages.append(message)
        session.last_activity = datetime.now()
        return message
    
    def get_conversation_messages(self, session_id: str):
        """Get conversation history in LangChain format"""
        from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
        
        session = self.sessions.get(session_id)
        if not session:
            return [SystemMessage(content="You are a helpful AI assistant.")]
        
        messages = [
            SystemMessage(content="You are a helpful AI assistant. Answer questions naturally and conversationally. When users ask about learning or courses, use your course search tools.")
        ]
        
        # Add conversation history (last 10 messages)
        for msg in session.messages[-10:]:
            if msg.message_type == "user":
                messages.append(HumanMessage(content=msg.content))
            elif msg.message_type == "assistant":
                messages.append(AIMessage(content=msg.content))
        
        return messages
    
    async def stream_response(self, session_id: str, user_message: str) -> AsyncGenerator[str, None]:
        """Stream agent response naturally"""
        
        logger.info(f"🎬 Stream start: session={session_id}, message='{user_message}'")
        
        try:
            # Add user message
            user_msg = self.add_message(session_id, "user", user_message)
            if user_msg:
                yield self._format_sse("message_added", user_msg)
            
            if not self.initialized:
                logger.warning("⚠️ Agent not initialized, using fallback")
        except:
            pass
    def _format_sse(self, event: str, data) -> str:
        """Format SSE"""
        if isinstance(data, ChatMessage):
            data = {
                "id": data.id,
                "session_id": data.session_id,
                "message_type": data.message_type,
                "content": data.content,
                "timestamp": data.timestamp.isoformat()
            }
        
        return f"data: {json.dumps({'event': event, 'data': data})}\n\n"

# Global agent
agent = CleanChatAgent()

# FastAPI app
app = FastAPI(title="Simple Grace Papers Chat")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await agent.initialize()

@app.get("/health")
async def health():
    return {"status": "healthy", "agent_ready": agent.initialized}

@app.post("/api/chat/start")
async def start_chat():
    session_id = agent.create_session()
    return {"success": True, "session_id": session_id}

@app.post("/api/chat/stream")
async def stream_chat(request: ChatRequest):
    return StreamingResponse(
        agent.stream_response(request.session_id, request.message),
        media_type="text/event-stream"
    )

@app.get("/demo-simple")
async def demo():
    return HTMLResponse('''
    <!DOCTYPE html>
    <html>
    <head><title>Simple Test</title></head>
    <body>
        <h1>Simple Chat Test</h1>
        <div id="messages" style="height:300px;overflow-y:auto;border:1px solid #ccc;padding:10px;margin:10px 0;"></div>
        <input id="input" placeholder="Type message..." style="width:70%;padding:10px;">
        <button onclick="send()" style="padding:10px;">Send</button>
        
        <div id="courses" style="margin-top:20px;padding:10px;border:1px solid #ddd;">
            <h3>Courses</h3>
            <div id="courseList">No courses yet</div>
        </div>
        
        <script>
            let sessionId = null;
            
            fetch('/api/chat/start', {method: 'POST'})
                .then(r => r.json())
                .then(data => sessionId = data.session_id);
            
            async function send() {
                const input = document.getElementById('input');
                const message = input.value.trim();
                if (!message) return;
                
                addMsg(message, 'user');
                input.value = '';
                
                const resp = await fetch('/api/chat/stream', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({session_id: sessionId, message})
                });
                
                const reader = resp.body.getReader();
                while (true) {
                    const {done, value} = await reader.read();
                    if (done) break;
                    
                    const chunk = new TextDecoder().decode(value);
                    for (const line of chunk.split('\n')) {
                        if (line.startsWith('data: ')) {
                            try {
                                const data = JSON.parse(line.slice(6));
                                if (data.event === 'message_added' && data.data.message_type === 'assistant') {
                                    addMsg(data.data.content, 'assistant');
                                }
                                if (data.event === 'courses_ready') {
                                    showCourses(data.data.courses);
                                }
                            } catch (e) {
                                console.error('Parse error:', e);
                            }
                        }
                    }
                }
            }
            
            function addMsg(content, type) {
                const div = document.createElement('div');
                div.style.margin = '5px 0';
                div.style.padding = '8px';
                div.style.background = type === 'user' ? '#e3f2fd' : '#f5f5f5';
                div.style.borderRadius = '5px';
                div.textContent = `${type}: ${content}`;
                document.getElementById('messages').appendChild(div);
            }
            
            function showCourses(courses) {
                const courseList = document.getElementById('courseList');
                if (!courses || courses.length === 0) {
                    courseList.innerHTML = 'No courses found';
                    return;
                }
                
                courseList.innerHTML = courses.map(course => 
                    `<div style="border:1px solid #ddd;padding:10px;margin:5px 0;">
                        <strong>${course.title || 'Untitled'}</strong><br>
                        <small>${course.partner_primary || 'Unknown'} - ${course.level || 'Any level'}</small>
                    </div>`
                ).join('');
            }
        </script>
    </body>
    </html>
    ''')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("simple_agent:app", host="0.0.0.0", port=8002, reload=True)
    
    def _is_tool_result(self, content: str) -> bool:
        """Check if content is a tool result (JSON data)"""
        if not content or len(content) < 10:
            return False
        
        content = content.strip()
        
        # Check if it looks like JSON
        if content.startswith('{') and content.endswith('}'):
            try:
                data = json.loads(content)
                # Check for tool result indicators
                if isinstance(data, dict) and any(key in data for key in ['success', 'courses', 'query', 'total_results']):
                    return True
            except:
                pass
        
        # Check for other tool result patterns
        tool_indicators = [
            '"success": true',
            '"courses":',
            '"total_results":',
            '"query":'
        ]
        
        return any(indicator in content for indicator in tool_indicators)
    
    def _is_obvious_system_content(self, content: str) -> bool:
        """Check if content is obviously system-generated (simplified filter)"""
        if not content:
            return False
        
        content_lower = content.lower().strip()
        
        # Only filter very obvious system content
        obvious_system_patterns = [
            "you are a helpful ai assistant",
            "follow this process:",
            "example workflow:",
            "important: when users ask"
        ]
        
        return any(pattern in content_lower for pattern in obvious_system_patterns)
    
    def _format_sse(self, event: str, data) -> str:
        """Format Server-Sent Event"""
        try:
            if isinstance(data, ChatMessage):
                data = {
                    "id": data.id,
                    "session_id": data.session_id,
                    "message_type": data.message_type,
                    "content": data.content,
                    "timestamp": data.timestamp.isoformat()
                }
            
            event_data = {
                "event": event,
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
            
            # Clean JSON formatting
            json_str = json.dumps(event_data, separators=(',', ':'), ensure_ascii=False)
            sse_line = f"data: {json_str}\n\n"
            
            return sse_line
            
        except Exception as e:
            logger.error(f"❌ SSE formatting error: {e}")
            # Return minimal error event
            error_json = json.dumps({"event": "format_error", "data": {"error": str(e)}})
            return f"data: {error_json}\n\n"

# Global agent
agent = CleanChatAgent()

# FastAPI app
app = FastAPI(title="Clean Grace Papers Chat", version="2.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await agent.initialize()

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "agent_initialized": agent.initialized,
        "tools_loaded": len(agent.tools) if agent.tools else 0
    }

@app.post("/api/chat/start")
async def start_chat():
    """Start new chat session"""
    session_id = agent.create_session()
    return {
        "success": True,
        "session_id": session_id,
        "message": "Chat session started"
    }

@app.post("/api/chat/stream")
async def stream_chat(request: ChatRequest):
    """Stream chat response"""
    return StreamingResponse(
        agent.stream_response(request.session_id, request.message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*"
        }
    )

@app.get("/api/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """Get chat history"""
    session = agent.sessions.get(session_id)
    if not session:
        return {"success": False, "error": "Session not found"}
    
    return {
        "success": True,
        "session_id": session_id,
        "messages": [msg.dict() for msg in session.messages],
        "total_messages": len(session.messages)
    }

@app.get("/demo-clean")
async def serve_clean_demo():
    """Serve clean demo"""
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Clean Chat Demo</title>
        <style>
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                max-width: 1200px; margin: 0 auto; padding: 20px; background: #f5f5f5;
            }
            .container { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; height: 80vh; }
            .panel { background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .messages { 
                height: 400px; overflow-y: auto; border: 1px solid #eee; 
                padding: 15px; margin: 15px 0; border-radius: 8px;
            }
            .message { margin: 10px 0; padding: 12px; border-radius: 8px; max-width: 80%; }
            .user { background: #007bff; color: white; margin-left: auto; }
            .assistant { background: #f8f9fa; border: 1px solid #dee2e6; }
            .input-area { display: flex; gap: 10px; }
            input { flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 6px; }
            button { padding: 12px 24px; background: #007bff; color: white; border: none; border-radius: 6px; cursor: pointer; }
            .course-card {
                border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin: 10px 0;
                background: #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .course-title { font-weight: bold; color: #333; margin-bottom: 8px; font-size: 1.1em; }
            .course-provider { color: #666; font-size: 0.9em; margin-bottom: 5px; }
            .course-level { 
                display: inline-block; background: #e3f2fd; color: #1976d2;
                padding: 4px 12px; border-radius: 12px; font-size: 0.8em; margin: 5px 0;
            }
            .course-description { color: #555; line-height: 1.4; margin: 8px 0; }
            .course-link { 
                display: inline-block; margin-top: 10px; padding: 8px 16px; 
                background: #007bff; color: white; text-decoration: none; 
                border-radius: 4px; font-size: 0.9em; 
            }
            .course-link:hover { background: #0056b3; }
            .status { padding: 10px; background: #e8f5e8; border-radius: 5px; margin: 10px 0; font-size: 0.9em; }
        </style>
    </head>
    <body>
        <h1>🤖 Clean Chat Demo</h1>
        <p>Natural conversation with course discovery</p>
        
        <div class="container">
            <div class="panel">
                <h3>💬 Chat</h3>
                <div id="status" class="status">Ready to chat!</div>
                <div id="messages" class="messages">
                    <div class="message assistant">Hello! I can help with any questions or find courses for you. What would you like to know?</div>
                </div>
                <div class="input-area">
                    <input type="text" id="messageInput" placeholder="Ask me anything...">
                    <button onclick="sendMessage()">Send</button>
                </div>
            </div>
            
            <div class="panel">
                <h3>📚 Course Recommendations</h3>
                <div id="coursesArea">
                    <p style="color: #666; text-align: center; padding: 40px;">
                        Ask about learning something to see course recommendations here!
                    </p>
                </div>
            </div>
        </div>
        
        <script>
            let sessionId = null;
            
            async function init() {
                try {
                    const response = await fetch('/api/chat/start', {method: 'POST'});
                    const result = await response.json();
                    sessionId = result.session_id;
                    console.log('✅ Chat session started:', sessionId);
                    document.getElementById('status').textContent = `Connected! Session: ${sessionId.slice(0, 8)}...`;
                } catch (error) {
                    console.error('Failed to start chat:', error);
                    document.getElementById('status').textContent = 'Failed to connect';
                }
            }
            
            async function sendMessage() {
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                if (!message || !sessionId) return;
                
                addMessage(message, 'user');
                input.value = '';
                document.getElementById('status').textContent = 'Processing...';
                
                try {
                    const response = await fetch('/api/chat/stream', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({session_id: sessionId, message})
                    });
                    
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}`);
                    }
                    
                    const reader = response.body.getReader();
                    
                    while (true) {
                        const {done, value} = await reader.read();
                        if (done) break;
                        
                        const chunk = new TextDecoder().decode(value);
                        const lines = chunk.split('\\n');
                        
                        for (const line of lines) {
                            if (line.startsWith('data: ') && line.length > 6) {
                                const jsonStr = line.slice(6).trim();
                                if (!jsonStr) continue;
                                
                                try {
                                    const data = JSON.parse(jsonStr);
                                    handleStreamEvent(data);
                                } catch (e) {
                                    console.warn('Parse error:', e, 'Raw:', jsonStr.slice(0, 100));
                                }
                            }
                        }
                    }
                } catch (error) {
                    console.error('Streaming error:', error);
                    addMessage('Sorry, I encountered an error. Please try again.', 'assistant');
                    document.getElementById('status').textContent = 'Error occurred';
                }
            }
            
            function handleStreamEvent(data) {
                console.log('📡 Event:', data.event, data.data);
                
                switch (data.event) {
                    case 'message_added':
                        if (data.data.message_type === 'assistant') {
                            addMessage(data.data.content, 'assistant');
                        }
                        break;
                        
                    case 'courses_ready':
                        displayCourseRecommendations(data.data);
                        break;
                        
                    case 'stream_complete':
                        console.log('✅ Stream completed');
                        document.getElementById('status').textContent = 'Ready to chat!';
                        break;
                        
                    case 'stream_error':
                        console.error('❌ Stream error:', data.data.error);
                        addMessage('I encountered an error. Please try again.', 'assistant');
                        break;
                }
            }
            
            function addMessage(content, type) {
                const div = document.createElement('div');
                div.className = `message ${type}`;
                div.textContent = content;
                document.getElementById('messages').appendChild(div);
                div.scrollIntoView({behavior: 'smooth'});
            }
            
            function displayCourseRecommendations(courseData) {
                console.log('📚 Displaying courses:', courseData);
                
                const coursesArea = document.getElementById('coursesArea');
                const courses = courseData.courses || [];
                
                if (courses.length === 0) {
                    coursesArea.innerHTML = `
                        <div style="padding: 20px; text-align: center; color: #666;">
                            <p>No courses found. Try refining your request!</p>
                        </div>
                    `;
                    return;
                }
                
                // Display course cards
                const courseCards = courses.map(course => {
                    const title = course.title || 'Untitled Course';
                    const provider = course.partner_primary || course.provider || 'Unknown Provider';
                    const level = course.level || 'All Levels';
                    const description = course.primary_description || course.description || 'No description available';
                    const platform = course.platform || 'Unknown';
                    
                    return `
                        <div class="course-card">
                            <div class="course-title">${title}</div>
                            <div class="course-provider">📚 ${provider}</div>
                            <div class="course-level">${level}</div>
                            <div class="course-description">${description.substring(0, 150)}...</div>
                            <div style="font-size: 0.8em; color: #888; margin-top: 8px;">Platform: ${platform}</div>
                            ${course.url ? `<a href="${course.url}" target="_blank" class="course-link">View Course</a>` : ''}
                        </div>
                    `;
                }).join('');
                
                coursesArea.innerHTML = `
                    <div style="margin-bottom: 15px;">
                        <h4 style="margin: 0; color: #2e7d32;">🎯 Found ${courses.length} Courses!</h4>
                        <p style="margin: 5px 0 0 0; color: #666; font-size: 0.9em;">Query: "${courseData.query || 'course search'}"</p>
                    </div>
                    ${courseCards}
                `;
            }
            
            // Initialize on page load
            document.addEventListener('DOMContentLoaded', init);
            
            // Send message on Enter
            document.getElementById('messageInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') sendMessage();
            });
        </script>
    </body>
    </html>
    '''
    return HTMLResponse(content=html)

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting Clean Chat Agent on port 8001")
    uvicorn.run(
        "clean_agent_chat:app",
        host="0.0.0.0", 
        port=8001, 
        reload=True,
        log_level="info"
    )
