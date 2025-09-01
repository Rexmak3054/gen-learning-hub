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
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Models
class ChatMessage(BaseModel):
    id: str
    session_id: str
    message_type: str
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

class SimpleChatAgent:
    def __init__(self):
        self.initialized = False
        self.sessions: Dict[str, ChatSession] = {}
        self.client = None
        self.graph = None
        self.tools = []
        
    async def initialize(self):
        """Initialize the agent"""
        try:
            logger.info("🔄 Initializing simple agent...")
            
            from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
            from langchain.chat_models import init_chat_model
            from langgraph.graph import StateGraph, START, MessagesState
            from langgraph.prebuilt import ToolNode, tools_condition
            from langchain_mcp_adapters.client import MultiServerMCPClient
            
            # MCP client
            current_dir = os.path.dirname(os.path.abspath(__file__))
            course_server_path = os.path.join(os.path.dirname(current_dir), "course_server.py")
            
            self.client = MultiServerMCPClient({
                "course": {
                    "command": "python",
                    "args": [course_server_path],
                    "transport": "stdio",
                },
            })
            
            self.tools = await self.client.get_tools()
            logger.info(f"✅ Tools: {[tool.name for tool in self.tools]}")
            
            # LLM
            self.llm = init_chat_model("openai:gpt-4o")
            
            # Simple graph
            def chatbot(state):
                return {"messages": [self.llm.bind_tools(self.tools).invoke(state["messages"])]}
            
            graph_builder = StateGraph(MessagesState)
            graph_builder.add_node("chatbot", chatbot)
            graph_builder.add_node("tools", ToolNode(self.tools))
            graph_builder.add_edge(START, "chatbot")
            graph_builder.add_conditional_edges("chatbot", tools_condition)
            graph_builder.add_edge("tools", "chatbot")
            
            self.graph = graph_builder.compile()
            
            self.initialized = True
            logger.info("🚀 Agent ready!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Init failed: {e}")
            return False
    
    def create_session(self) -> str:
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = ChatSession(
            id=session_id,
            created_at=datetime.now(),
            last_activity=datetime.now()
        )
        return session_id
    
    def add_message(self, session_id: str, message_type: str, content: str) -> Optional[ChatMessage]:
        session = self.sessions.get(session_id)
        if not session:
            return None
            
        message = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=session_id,
            message_type=message_type,
            content=content,
            timestamp=datetime.now()
        )
        
        session.messages.append(message)
        return message
    
    async def stream_response(self, session_id: str, user_message: str) -> AsyncGenerator[str, None]:
        """Stream response with simplified logic"""
        
        logger.info(f"🎬 Processing: '{user_message}'")
        
        # Add user message
        user_msg = self.add_message(session_id, "user", user_message)
        yield self._format_sse("message_added", user_msg)
        
        if not self.initialized:
            response = "Hello! I'm here to help."
            assistant_msg = self.add_message(session_id, "assistant", response)
            yield self._format_sse("message_added", assistant_msg)
            yield self._format_sse("stream_complete", {"session_id": session_id})
            return
        
        try:
            from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
            
            # Build context with just the current conversation
            session = self.sessions.get(session_id)
            messages = [
                SystemMessage(content="You are a helpful AI assistant. Answer naturally. When users ask about courses, use your course search tools.")
            ]
            
            # Add recent history (last 6 messages to keep context manageable)
            if session:
                for msg in session.messages[-6:]:
                    if msg.message_type == "user":
                        messages.append(HumanMessage(content=msg.content))
                    elif msg.message_type == "assistant":
                        messages.append(AIMessage(content=msg.content))
            
            # Add current message
            messages.append(HumanMessage(content=user_message))
            
            logger.info(f"🤖 Running agent with {len(messages)} messages")
            
            # Run agent
            result = await self.graph.ainvoke({"messages": messages})
            
            if result and "messages" in result:
                # Get the last message (should be the agent's response)
                last_message = result["messages"][-1]
                
                if hasattr(last_message, 'content') and last_message.content:
                    content = last_message.content
                    logger.info(f"🎯 Agent response: '{content[:60]}...'")
                    
                    # Only filter out obvious JSON tool results
                    if not (content.strip().startswith('{') and '"courses"' in content):
                        assistant_msg = self.add_message(session_id, "assistant", content)
                        yield self._format_sse("message_added", assistant_msg)
                    else:
                        logger.info("🔧 Filtered JSON tool result")
                
                # Look for course data in any message
                for message in result["messages"]:
                    if hasattr(message, 'content') and message.content:
                        if self._extract_course_data(message.content, user_message):
                            # Course data found and sent
                            pass
            
            yield self._format_sse("stream_complete", {"session_id": session_id})
            
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            error_msg = self.add_message(session_id, "assistant", "Sorry, I had an issue. Please try again.")
            yield self._format_sse("message_added", error_msg)
    
    async def _extract_course_data(self, content: str, user_message: str) -> bool:
        """Extract and send course data if found"""
        try:
            if content.strip().startswith('{') and '"courses"' in content:
                tool_data = json.loads(content.strip())
                if isinstance(tool_data, dict) and 'courses' in tool_data:
                    courses = tool_data['courses']
                    if courses:
                        logger.info(f"📚 Sending {len(courses)} courses to frontend")
                        
                        yield self._format_sse("courses_ready", {
                            "courses": courses,
                            "total_results": len(courses),
                            "query": user_message
                        })
                        return True
        except:
            pass
        return False
    
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
        
        return f"data: {json.dumps({'event': event, 'data': data})}\\n\\n"

# App
agent = SimpleChatAgent()
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
                    for (const line of chunk.split('\\n')) {
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
