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
import openai

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple chat models
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

# Simple course search (reuse existing logic)
class SimpleCourseSearch:
    def __init__(self):
        self.initialized = False
        
    async def initialize(self):
        """Simple initialization"""
        self.initialized = True
        logger.info("✅ Course search initialized")
        
    async def search_courses(self, query: str, k: int = 5):
        """Simple course search - you can integrate your existing course search here"""
        # Mock courses for now - replace with your actual course search
        mock_courses = [
            {
                "uuid": f"course-{i+1}",
                "title": f"{query.title()} Course {i+1}",
                "provider": "Mock University",
                "level": "Intermediate",
                "skills": [query.title(), "Learning"],
                "description": f"A comprehensive course about {query}",
                "platform": "coursera",
                "similarity_score": 0.9 - (i * 0.1)
            }
            for i in range(k)
        ]
        
        return {
            "success": True,
            "courses": mock_courses,
            "total_results": len(mock_courses),
            "query": query
        }

# Simple chat manager
class SimpleChatManager:
    def __init__(self):
        self.sessions: Dict[str, ChatSession] = {}
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.course_search = SimpleCourseSearch()
        
    async def initialize(self):
        await self.course_search.initialize()
        
    def create_session(self) -> str:
        """Create new chat session"""
        session_id = str(uuid.uuid4())
        session = ChatSession(
            id=session_id,
            created_at=datetime.now(),
            last_activity=datetime.now()
        )
        self.sessions[session_id] = session
        return session_id
    
    def add_message(self, session_id: str, message_type: str, content: str) -> ChatMessage:
        """Add message to session"""
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
        session.last_activity = datetime.now()
        return message
    
    def get_conversation_history(self, session_id: str) -> List[Dict]:
        """Get conversation history for OpenAI API"""
        session = self.sessions.get(session_id)
        if not session:
            return []
        
        # Convert to OpenAI format
        history = []
        for msg in session.messages[-10:]:  # Last 10 messages
            if msg.message_type == "user":
                history.append({"role": "user", "content": msg.content})
            elif msg.message_type == "assistant":
                history.append({"role": "assistant", "content": msg.content})
        
        return history
    
    def is_course_related(self, message: str) -> bool:
        """Simple course detection"""
        course_keywords = [
            'learn', 'course', 'study', 'training', 'education', 'skill',
            'programming', 'python', 'javascript', 'web development', 
            'data science', 'machine learning', 'ai courses', 'tutorial'
        ]
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in course_keywords)
    
    async def stream_chat_response(self, session_id: str, user_message: str) -> AsyncGenerator[str, None]:
        """Stream a natural chat response"""
        
        # Add user message
        user_msg = self.add_message(session_id, "user", user_message)
        yield self._format_sse("message_added", user_msg)
        
        try:
            # Get conversation history
            history = self.get_conversation_history(session_id)
            
            # Simple system message
            messages = [
                {"role": "system", "content": "You are a helpful AI assistant. Answer questions naturally and conversationally."}
            ]
            messages.extend(history)
            messages.append({"role": "user", "content": user_message})
            
            # Get LLM response
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                stream=False,  # Start with non-streaming for simplicity
                temperature=0.7
            )
            
            assistant_response = response.choices[0].message.content
            
            # Add assistant message
            assistant_msg = self.add_message(session_id, "assistant", assistant_response)
            yield self._format_sse("message_added", assistant_msg)
            
            # Check if we need to search for courses
            if self.is_course_related(user_message):
                yield self._format_sse("searching_courses", {"query": user_message})
                
                # Search for courses
                course_result = await self.course_search.search_courses(user_message)
                
                if course_result["success"] and course_result["courses"]:
                    yield self._format_sse("courses_ready", {
                        "courses": course_result["courses"],
                        "total_results": course_result["total_results"],
                        "query": user_message,
                        "session_id": session_id
                    })
            
            yield self._format_sse("stream_complete", {"session_id": session_id})
            
        except Exception as e:
            logger.error(f"Chat error: {e}")
            error_msg = self.add_message(session_id, "assistant", "I'm having trouble right now. Please try again.")
            yield self._format_sse("message_added", error_msg)
            yield self._format_sse("stream_error", {"error": str(e)})
    
    def _format_sse(self, event: str, data) -> str:
        """Format Server-Sent Event"""
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
        
        return f"data: {json.dumps(event_data)}\\n\\n"

# Global chat manager
chat_manager = SimpleChatManager()

# Create FastAPI app
app = FastAPI(title="Simple Grace Papers Chat", version="2.0.0")

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
    await chat_manager.initialize()

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "2.0.0"}

@app.post("/api/chat/start")
async def start_chat():
    """Start new chat session"""
    session_id = chat_manager.create_session()
    return {
        "success": True,
        "session_id": session_id,
        "message": "Chat started successfully"
    }

@app.post("/api/chat/stream")
async def stream_chat(request: ChatRequest):
    """Stream chat response"""
    return StreamingResponse(
        chat_manager.stream_chat_response(request.session_id, request.message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*"
        }
    )

@app.get("/demo-simple")
async def serve_simple_demo():
    """Serve simple demo"""
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Simple Chat Demo</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .messages { height: 400px; overflow-y: auto; border: 1px solid #ccc; padding: 10px; margin: 10px 0; }
            .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
            .user { background: #e3f2fd; margin-left: 50px; }
            .assistant { background: #f3e5f5; margin-right: 50px; }
            .input-area { display: flex; gap: 10px; }
            input { flex: 1; padding: 10px; }
            button { padding: 10px 20px; }
        </style>
    </head>
    <body>
        <h1>🤖 Simple Chat Demo</h1>
        <div id="messages" class="messages"></div>
        <div class="input-area">
            <input type="text" id="messageInput" placeholder="Ask me anything...">
            <button onclick="sendMessage()">Send</button>
        </div>
        
        <script>
            let sessionId = null;
            
            async function init() {
                const response = await fetch('/api/chat/start', {method: 'POST'});
                const result = await response.json();
                sessionId = result.session_id;
                console.log('Chat started:', sessionId);
            }
            
            async function sendMessage() {
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                if (!message) return;
                
                addMessage(message, 'user');
                input.value = '';
                
                const response = await fetch('/api/chat/stream', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({session_id: sessionId, message})
                });
                
                const reader = response.body.getReader();
                
                while (true) {
                    const {done, value} = await reader.read();
                    if (done) break;
                    
                    const chunk = new TextDecoder().decode(value);
                    const lines = chunk.split('\\n');
                    
                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            try {
                                const data = JSON.parse(line.slice(6));
                                handleEvent(data);
                            } catch (e) {
                                console.error('Parse error:', e);
                            }
                        }
                    }
                }
            }
            
            function handleEvent(data) {
                console.log('Event:', data);
                
                if (data.event === 'message_added' && data.data.message_type === 'assistant') {
                    addMessage(data.data.content, 'assistant');
                }
                else if (data.event === 'courses_ready') {
                    addMessage(`Found ${data.data.courses.length} courses!`, 'assistant');
                }
            }
            
            function addMessage(content, type) {
                const div = document.createElement('div');
                div.className = `message ${type}`;
                div.textContent = content;
                document.getElementById('messages').appendChild(div);
                div.scrollIntoView();
            }
            
            init();
        </script>
    </body>
    </html>
    '''
    return HTMLResponse(content=html)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)