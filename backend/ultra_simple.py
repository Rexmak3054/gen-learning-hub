from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, HTMLResponse
from pydantic import BaseModel
import uuid
import json
import logging
from datetime import datetime
from typing import AsyncGenerator, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatRequest(BaseModel):
    session_id: str
    message: str

class SimpleAgent:
    def __init__(self):
        self.sessions = {}
        self.initialized = False
        self.graph = None
        
    async def initialize(self):
        try:
            logger.info("🔄 Initializing...")
            
            from langchain_core.messages import HumanMessage, SystemMessage
            from langchain.chat_models import init_chat_model
            from langgraph.graph import StateGraph, START, MessagesState
            from langgraph.prebuilt import ToolNode, tools_condition
            from langchain_mcp_adapters.client import MultiServerMCPClient
            import os
            
            # MCP client
            course_server_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "course_server.py")
            
            self.client = MultiServerMCPClient({
                "course": {
                    "command": "python",
                    "args": [course_server_path],
                    "transport": "stdio",
                }
            })
            
            self.tools = await self.client.get_tools()
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
            logger.info("✅ Ready!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Init failed: {e}")
            return False
    
    def create_session(self):
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = []
        return session_id
    
    async def chat(self, session_id: str, user_message: str) -> AsyncGenerator[str, None]:
        """Simple chat with course detection"""
        
        # Add user message to session
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        
        yield self._sse("message_added", {
            "message_type": "user", 
            "content": user_message,
            "timestamp": datetime.now().isoformat()
        })
        
        if not self.initialized:
            yield self._sse("message_added", {
                "message_type": "assistant",
                "content": "Hello! I'm here to help.",
                "timestamp": datetime.now().isoformat()
            })
            yield self._sse("stream_complete", {"session_id": session_id})
            return
        
        try:
            from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
            
            # Build simple context
            messages = [
                SystemMessage(content="You are a helpful AI assistant. Answer naturally. Use course tools when users ask about learning.")
            ]
            
            # Add recent history
            for msg in self.sessions[session_id][-6:]:
                if msg.get("type") == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg.get("type") == "assistant":
                    messages.append(AIMessage(content=msg["content"]))
            
            # Add current message
            messages.append(HumanMessage(content=user_message))
            
            logger.info(f"🤖 Running agent with {len(messages)} messages")
            
            # Run agent
            result = await self.graph.ainvoke({"messages": messages})
            
            # Process response
            if result and "messages" in result:
                # Get the agent's response (should be the last message)
                agent_response = result["messages"][-1]
                
                if hasattr(agent_response, 'content') and agent_response.content:
                    content = agent_response.content
                    
                    # Check if this is course data (JSON)
                    if content.strip().startswith('{') and '"courses"' in content:
                        try:
                            course_data = json.loads(content)
                            if 'courses' in course_data:
                                courses = course_data['courses']
                                logger.info(f"📚 Found {len(courses)} courses")
                                
                                # Send course data
                                yield self._sse("courses_ready", {
                                    "courses": courses,
                                    "total_results": len(courses),
                                    "query": user_message
                                })
                                
                                # Send natural response about courses
                                natural_response = f"I found {len(courses)} great courses for you!"
                                yield self._sse("message_added", {
                                    "message_type": "assistant",
                                    "content": natural_response,
                                    "timestamp": datetime.now().isoformat()
                                })
                                
                                # Save to session
                                self.sessions[session_id].extend([
                                    {"type": "user", "content": user_message},
                                    {"type": "assistant", "content": natural_response}
                                ])
                        except:
                            # Not valid JSON, treat as normal response
                            yield self._sse("message_added", {
                                "message_type": "assistant",
                                "content": content,
                                "timestamp": datetime.now().isoformat()
                            })
                            
                            self.sessions[session_id].extend([
                                {"type": "user", "content": user_message},
                                {"type": "assistant", "content": content}
                            ])
                    else:
                        # Normal conversation response
                        yield self._sse("message_added", {
                            "message_type": "assistant",
                            "content": content,
                            "timestamp": datetime.now().isoformat()
                        })
                        
                        self.sessions[session_id].extend([
                            {"type": "user", "content": user_message},
                            {"type": "assistant", "content": content}
                        ])
            
            yield self._sse("stream_complete", {"session_id": session_id})
            
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            yield self._sse("message_added", {
                "message_type": "assistant",
                "content": "Sorry, I had an issue. Please try again.",
                "timestamp": datetime.now().isoformat()
            })
    
    def _sse(self, event: str, data) -> str:
        return f"data: {json.dumps({'event': event, 'data': data})}\\n\\n"

agent = SimpleAgent()
app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
async def startup():
    await agent.initialize()

@app.get("/health")
async def health():
    return {"status": "ok", "ready": agent.initialized}

@app.post("/api/chat/start")
async def start():
    return {"session_id": agent.create_session()}

@app.post("/api/chat/stream")
async def stream(request: ChatRequest):
    return StreamingResponse(
        agent.chat(request.session_id, request.message),
        media_type="text/event-stream"
    )

@app.get("/demo")
async def demo():
    return HTMLResponse('''
    <html><head><title>Simple Chat</title></head><body>
        <h1>🤖 Simple Chat Test</h1>
        <div id="msgs" style="height:300px;overflow-y:auto;border:1px solid #ccc;padding:10px;margin:10px 0;"></div>
        <input id="inp" style="width:70%;padding:8px;" placeholder="Say hello or ask about courses...">
        <button onclick="send()">Send</button>
        
        <div style="margin-top:20px;">
            <h3>📚 Courses</h3>
            <div id="courses">Ask about learning to see courses here</div>
        </div>
        
        <script>
            let sid = null;
            fetch('/api/chat/start', {method:'POST'}).then(r=>r.json()).then(d=>sid=d.session_id);
            
            async function send() {
                const inp = document.getElementById('inp');
                if (!inp.value.trim()) return;
                
                add(inp.value, 'user');
                const msg = inp.value;
                inp.value = '';
                
                const r = await fetch('/api/chat/stream', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({session_id: sid, message: msg})
                });
                
                const reader = r.body.getReader();
                while (true) {
                    const {done, value} = await reader.read();
                    if (done) break;
                    
                    const chunk = new TextDecoder().decode(value);
                    for (const line of chunk.split('\\n')) {
                        if (line.startsWith('data: ')) {
                            try {
                                const data = JSON.parse(line.slice(6));
                                if (data.event === 'message_added' && data.data.message_type === 'assistant') {
                                    add(data.data.content, 'assistant');
                                }
                                if (data.event === 'courses_ready') {
                                    showCourses(data.data.courses);
                                }
                            } catch (e) {
                                console.log('Parse error:', e);
                            }
                        }
                    }
                }
            }
            
            function add(content, type) {
                const div = document.createElement('div');
                div.style.margin = '5px';
                div.style.padding = '8px';
                div.style.background = type === 'user' ? '#e3f2fd' : '#f5f5f5';
                div.style.borderRadius = '4px';
                div.textContent = type + ': ' + content;
                document.getElementById('msgs').appendChild(div);
                div.scrollIntoView();
            }
            
            function showCourses(courses) {
                if (!courses?.length) return;
                const html = courses.map(c => 
                    `<div style="border:1px solid #ddd;padding:8px;margin:4px 0;">
                        <b>${c.title || 'Course'}</b><br>
                        <small>${c.partner_primary || 'Provider'} - ${c.level || 'Level'}</small>
                    </div>`
                ).join('');
                document.getElementById('courses').innerHTML = html;
            }
            
            document.getElementById('inp').addEventListener('keypress', e => {
                if (e.key === 'Enter') send();
            });
        </script>
    </body></html>
    ''')

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Simple Agent on port 8002")
    print("Demo: http://localhost:8002/demo")
    uvicorn.run("ultra_simple:app", host="0.0.0.0", port=8002, reload=True)
