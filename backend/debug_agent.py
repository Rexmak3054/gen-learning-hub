from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, HTMLResponse
from pydantic import BaseModel
import uuid
import json
import logging
from datetime import datetime
from typing import AsyncGenerator

# Enhanced logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ChatRequest(BaseModel):
    session_id: str
    message: str

class DebugAgent:
    def __init__(self):
        self.sessions = {}
        self.initialized = False
        self.graph = None
        self.llm = None
        self.tools = []
        
    async def initialize(self):
        """Initialize with detailed logging"""
        try:
            logger.info("🔄 Starting initialization...")
            
            # Test OpenAI key
            import os
            openai_key = os.getenv("OPENAI_API_KEY")
            if not openai_key:
                logger.error("❌ No OPENAI_API_KEY found!")
                return False
            logger.info(f"✅ OpenAI key found: {openai_key[:10]}...")
            
            # Import components
            logger.info("📦 Importing LangChain components...")
            from langchain_core.messages import HumanMessage, SystemMessage
            from langchain.chat_models import init_chat_model
            from langgraph.graph import StateGraph, START, MessagesState
            from langgraph.prebuilt import ToolNode, tools_condition
            from langchain_mcp_adapters.client import MultiServerMCPClient
            logger.info("✅ Imports successful")
            
            # MCP client
            logger.info("🔗 Setting up MCP client...")
            course_server_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "course_server.py")
            logger.info(f"📂 Course server path: {course_server_path}")
            logger.info(f"📁 File exists: {os.path.exists(course_server_path)}")
            
            self.client = MultiServerMCPClient({
                "course": {
                    "command": "python",
                    "args": [course_server_path],
                    "transport": "stdio",
                }
            })
            logger.info("✅ MCP client created")
            
            # Get tools
            logger.info("🛠️ Loading tools...")
            self.tools = await self.client.get_tools()
            logger.info(f"✅ Loaded {len(self.tools)} tools:")
            for tool in self.tools:
                logger.info(f"   - {tool.name}: {tool.description[:50]}...")
            
            # LLM
            logger.info("🧠 Initializing LLM...")
            self.llm = init_chat_model("openai:gpt-4o")
            logger.info("✅ LLM ready")
            
            # Test basic LLM call
            logger.info("🧪 Testing basic LLM call...")
            test_result = self.llm.invoke([HumanMessage(content="Hello")])
            logger.info(f"✅ LLM test: '{test_result.content[:30]}...'")
            
            # Build graph
            logger.info("🏗️ Building graph...")
            
            def chatbot(state):
                logger.debug(f"🤖 Chatbot node called with {len(state['messages'])} messages")
                try:
                    result = self.llm.bind_tools(self.tools).invoke(state["messages"])
                    logger.debug(f"🎯 Chatbot result: {type(result)}, content_len={len(result.content) if hasattr(result, 'content') else 0}")
                    return {"messages": [result]}
                except Exception as e:
                    logger.error(f"❌ Chatbot node error: {e}")
                    raise
            
            graph_builder = StateGraph(MessagesState)
            graph_builder.add_node("chatbot", chatbot)
            graph_builder.add_node("tools", ToolNode(self.tools))
            graph_builder.add_edge(START, "chatbot")
            graph_builder.add_conditional_edges("chatbot", tools_condition)
            graph_builder.add_edge("tools", "chatbot")
            
            self.graph = graph_builder.compile()
            logger.info("✅ Graph compiled")
            
            # Test graph
            logger.info("🧪 Testing graph execution...")
            test_result = await self.graph.ainvoke({
                "messages": [
                    SystemMessage(content="You are helpful."),
                    HumanMessage(content="Hello!")
                ]
            })
            logger.info(f"✅ Graph test successful: {len(test_result['messages'])} messages")
            
            self.initialized = True
            logger.info("🚀 Agent fully initialized!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def create_session(self):
        session_id = str(uuid.uuid4())[:8]  # Short ID for easier debugging
        self.sessions[session_id] = []
        logger.info(f"💬 Created session: {session_id}")
        return session_id
    
    async def chat(self, session_id: str, user_message: str) -> AsyncGenerator[str, None]:
        """Debug chat with detailed logging"""
        
        logger.info(f"🎬 CHAT START: session={session_id}, message='{user_message}'")
        
        # User message
        yield f"data: {json.dumps({'event': 'message_added', 'data': {'message_type': 'user', 'content': user_message}})}\\n\\n"
        
        if not self.initialized:
            logger.warning("⚠️ Agent not initialized!")
            yield f"data: {json.dumps({'event': 'message_added', 'data': {'message_type': 'assistant', 'content': 'Agent not ready'}})}\\n\\n"
            return
        
        try:
            from langchain_core.messages import HumanMessage, SystemMessage
            
            # Simple messages
            messages = [
                SystemMessage(content="You are a helpful AI assistant."),
                HumanMessage(content=user_message)
            ]
            
            logger.info(f"🤖 Calling graph with {len(messages)} messages...")
            logger.debug(f"Messages: {[type(m).__name__ + ': ' + m.content[:30] for m in messages]}")
            
            # Call the graph
            result = await self.graph.ainvoke({"messages": messages})
            
            logger.info(f"🎯 Graph result received!")
            logger.info(f"   Result type: {type(result)}")
            logger.info(f"   Result keys: {list(result.keys()) if result else 'None'}")
            
            if result and "messages" in result:
                messages_result = result["messages"]
                logger.info(f"   📝 Messages in result: {len(messages_result)}")
                
                for i, msg in enumerate(messages_result):
                    logger.info(f"   Message {i}: {type(msg).__name__}")
                    if hasattr(msg, 'content'):
                        content = msg.content or ""
                        logger.info(f"      Content: '{content[:100]}...'")
                        logger.info(f"      Content length: {len(content)}")
                        logger.info(f"      Is empty: {not content.strip()}")
                    
                    if hasattr(msg, 'tool_calls'):
                        tool_calls = msg.tool_calls or []
                        logger.info(f"      Tool calls: {len(tool_calls)}")
                
                # Find the last agent response
                last_message = messages_result[-1] if messages_result else None
                
                if last_message and hasattr(last_message, 'content'):
                    content = last_message.content
                    logger.info(f"🎯 AGENT RESPONSE: '{content}'")
                    
                    if content and content.strip():
                        # Send the response
                        yield f"data: {json.dumps({'event': 'message_added', 'data': {'message_type': 'assistant', 'content': content}})}\\n\\n"
                        logger.info("✅ Response sent to frontend")
                    else:
                        logger.warning("⚠️ Agent response is empty!")
                        yield f"data: {json.dumps({'event': 'message_added', 'data': {'message_type': 'assistant', 'content': 'I got an empty response. Please try again.'}})}\\n\\n"
                else:
                    logger.warning("⚠️ No content in last message!")
                    yield f"data: {json.dumps({'event': 'message_added', 'data': {'message_type': 'assistant', 'content': 'No response generated. Please try again.'}})}\\n\\n"
            else:
                logger.warning("⚠️ No messages in result!")
                yield f"data: {json.dumps({'event': 'message_added', 'data': {'message_type': 'assistant', 'content': 'No result from agent. Please try again.'}})}\\n\\n"
            
            yield f"data: {json.dumps({'event': 'stream_complete', 'data': {'session_id': session_id}})}\\n\\n"
            
        except Exception as e:
            logger.error(f"❌ Chat error: {e}")
            import traceback
            traceback.print_exc()
            
            yield f"data: {json.dumps({'event': 'message_added', 'data': {'message_type': 'assistant', 'content': f'Error: {str(e)}'}})}\\n\\n"

# App
agent = DebugAgent()
app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup") 
async def startup():
    success = await agent.initialize()
    logger.info(f"🚀 Startup complete: {success}")

@app.get("/health")
async def health():
    return {
        "status": "ok", 
        "initialized": agent.initialized,
        "tools": len(agent.tools),
        "tool_names": [t.name for t in agent.tools] if agent.tools else []
    }

@app.post("/api/chat/start")
async def start():
    session_id = agent.create_session()
    return {"session_id": session_id}

@app.post("/api/chat/stream")
async def stream(request: ChatRequest):
    return StreamingResponse(
        agent.chat(request.session_id, request.message),
        media_type="text/event-stream"
    )

@app.get("/debug")
async def debug_page():
    return HTMLResponse('''
    <html>
    <head><title>Debug Agent</title></head>
    <body>
        <h1>🔍 Debug Agent</h1>
        <button onclick="testHealth()">Test Health</button>
        <button onclick="testSimple()">Test Simple Message</button>
        <button onclick="testCourse()">Test Course Request</button>
        
        <div id="results" style="margin:20px 0; padding:10px; border:1px solid #ccc; height:400px; overflow-y:auto; font-family:monospace; font-size:12px;"></div>
        
        <script>
            let sessionId = null;
            
            async function testHealth() {
                log('Testing health...');
                const resp = await fetch('/health');
                const data = await resp.json();
                log('Health: ' + JSON.stringify(data, null, 2));
            }
            
            async function testSimple() {
                log('Testing simple message...');
                await sendMessage('Hello!');
            }
            
            async function testCourse() {
                log('Testing course request...');
                await sendMessage('I want to learn Python');
            }
            
            async function sendMessage(message) {
                if (!sessionId) {
                    const startResp = await fetch('/api/chat/start', {method: 'POST'});
                    const startData = await startResp.json();
                    sessionId = startData.session_id;
                    log('Session created: ' + sessionId);
                }
                
                log('Sending: ' + message);
                
                const resp = await fetch('/api/chat/stream', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({session_id: sessionId, message})
                });
                
                log('Response status: ' + resp.status);
                
                const reader = resp.body.getReader();
                while (true) {
                    const {done, value} = await reader.read();
                    if (done) break;
                    
                    const chunk = new TextDecoder().decode(value);
                    log('Raw chunk: ' + chunk);
                    
                    for (const line of chunk.split('\\n')) {
                        if (line.startsWith('data: ')) {
                            try {
                                const data = JSON.parse(line.slice(6));
                                log('Event: ' + JSON.stringify(data, null, 2));
                            } catch (e) {
                                log('Parse error: ' + e);
                            }
                        }
                    }
                }
            }
            
            function log(message) {
                const div = document.createElement('div');
                div.textContent = new Date().toISOString() + ': ' + message;
                document.getElementById('results').appendChild(div);
                div.scrollIntoView();
            }
        </script>
    </body>
    </html>
    ''')

if __name__ == "__main__":
    import uvicorn
    print("🔍 Starting Debug Agent on port 8003")
    print("Visit: http://localhost:8003/debug")
    uvicorn.run("debug_agent:app", host="0.0.0.0", port=8003, reload=True)
