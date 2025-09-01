from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, HTMLResponse
from pydantic import BaseModel
import uuid
import json
import logging
from datetime import datetime
from typing import AsyncGenerator
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatRequest(BaseModel):
    session_id: str
    message: str

class WorkingAgent:
    def __init__(self):
        self.sessions = {}
        self.initialized = False
        self.graph = None
        
    async def initialize(self):
        try:
            logger.info("🔄 Initializing working agent...")
            
            from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
            from langchain.chat_models import init_chat_model
            from langgraph.graph import StateGraph, START, MessagesState
            from langgraph.prebuilt import ToolNode, tools_condition
            from langchain_mcp_adapters.client import MultiServerMCPClient
            import os
            
            # MCP client
            course_server_path = os.path.join(os.path.dirname(__file__), "course_server.py")
            
            self.client = MultiServerMCPClient({
                "course": {
                    "command": "python",
                    "args": [course_server_path],
                    "transport": "stdio",
                }
            })
            
            self.tools = await self.client.get_tools()
            self.llm = init_chat_model("openai:gpt-4o")
            
            # Graph
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
            logger.info("✅ Working agent ready!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed: {e}")
            return False
    
    def create_session(self):
        session_id = str(uuid.uuid4())[:8]
        self.sessions[session_id] = []
        return session_id
    
    async def chat(self, session_id: str, user_message: str) -> AsyncGenerator[str, None]:
        """Working chat implementation with improved message filtering"""
        
        logger.info(f"🎬 Processing: '{user_message}'")
        
        # User message
        yield self._sse("message_added", {
            "message_type": "user", 
            "content": user_message,
            "timestamp": datetime.now().isoformat()
        })
        
        if not self.initialized:
            yield self._sse("message_added", {
                "message_type": "assistant",
                "content": "Hello! I'm here to help you.",
                "timestamp": datetime.now().isoformat()
            })
            return
        
        try:
            from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
            
            # Build context
            messages = [
                SystemMessage(content="You are a helpful AI assistant. Answer naturally. When users ask about courses, use your course search tools. you need to call the tool get_recommended_course_details at the end to pass your recommended course uuid to it and return the data to the backend ")
            ]
            
            # Add recent history
            for msg in self.sessions[session_id][-6:]:
                if msg.get("type") == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg.get("type") == "assistant":
                    messages.append(AIMessage(content=msg["content"]))
            
            messages.append(HumanMessage(content=user_message))
            
            logger.info(f"🤖 Running agent...")
            result = await self.graph.ainvoke({"messages": messages})
            
            if result and "messages" in result:
                messages_result = result["messages"]
                logger.info(f"📝 Got {len(messages_result)} messages back")
                
                # Process course data from tool messages (separate from final response)
                async for sse_event in self._handle_course_data(messages_result, user_message):
                    yield sse_event
                
                # Get the final assistant response
                final_response = self._get_final_assistant_response(messages_result)
                
                if final_response:
                    logger.info(f"💬 Final assistant response: '{final_response[:60]}...'")
                    
                    yield self._sse("message_added", {
                        "message_type": "assistant",
                        "content": final_response,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # Save only meaningful conversation to session history
                    self.sessions[session_id].extend([
                        {"type": "user", "content": user_message},
                        {"type": "assistant", "content": final_response}
                    ])
                else:
                    logger.warning("⚠️ No valid assistant response found")
                    yield self._sse("message_added", {
                        "message_type": "assistant",
                        "content": "I'm processing your request...",
                        "timestamp": datetime.now().isoformat()
                    })
            
            yield self._sse("stream_complete", {"session_id": session_id})
            
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            yield self._sse("message_added", {
                "message_type": "assistant",
                "content": f"Error occurred: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })
    
    async def _handle_course_data(self, messages_result, user_message) -> AsyncGenerator[str, None]:
        """Extract and handle course data from get_recommended_course_details tool calls"""
        for msg in messages_result:
            # Check if this is a tool message from get_recommended_course_details
            logger.info(f'calling final message: {msg}')
            if isinstance(msg, ToolMessage) and hasattr(msg, 'tool_call_id'):
                # Check if the tool call was get_recommended_course_details
                if hasattr(msg, 'name') and msg.name == 'get_recommended_course_details':
                    async for sse_event in self._process_course_tool_result(msg.content, user_message):
                        yield sse_event
                # Fallback: check tool_call_id or content for course tool pattern
                elif 'course' in str(msg.tool_call_id).lower() or self._is_course_tool_result(msg.content):
                    async for sse_event in self._process_course_tool_result(msg.content, user_message):
                        yield sse_event
    
    async def _process_course_tool_result(self, content, user_message) -> AsyncGenerator[str, None]:
        """Process content from get_recommended_course_details tool result"""
        if not content or not isinstance(content, str):
            return
            
        content = content.strip()
        
        # Try to parse as JSON
        try:
            course_json = json.loads(content)
            if 'courses' in course_json and course_json['courses']:
                logger.info(f"📚 Found course data with {len(course_json['courses'])} courses from tool call")
                
                # Send course data to frontend
                yield self._sse("courses_ready", {
                    "courses": course_json['courses'],
                    "total_results": len(course_json['courses']),
                    "query": user_message
                })
        except json.JSONDecodeError:
            # If not JSON, check if it's a plain text response with course info
            if 'course' in content.lower() and ('title' in content.lower() or 'code' in content.lower()):
                logger.info("📚 Found course data in text format from tool call")
                # Could add text parsing logic here if needed
    
    def _is_course_tool_result(self, content):
        """Check if content appears to be from a course-related tool call"""
        if not content or not isinstance(content, str):
            return False
        
        content = content.strip()
        
        # Check for course-specific JSON structure
        if content.startswith('{') and '"courses"' in content:
            return True
            
        # Check for course-related keywords in structured content
        if ('course' in content.lower() and 
            any(keyword in content.lower() for keyword in ['credits', 'prerequisite', 'semester', 'department'])):
            return True
            
        return False
    
    def _get_final_assistant_response(self, messages_result):
        """Get the final assistant response using proper message type filtering"""
        from langchain_core.messages import AIMessage
        
        # Find all AI messages with non-empty content
        ai_messages = []
        for msg in messages_result:
            if isinstance(msg, AIMessage) and hasattr(msg, 'content') and msg.content:
                content = msg.content.strip()
                if content:  # Non-empty content
                    ai_messages.append(content)
        
        if not ai_messages:
            logger.warning("No AI messages found in result")
            return None
        
        # Get the last AI message (final response after all tool calls)
        final_response = ai_messages[-1]
        
        # Basic sanity checks - only filter out obviously invalid responses
        if (len(final_response) < 2 or  # Very short responses
            self._is_structured_data(final_response)):  # JSON/structured data
            
            logger.info(f"Final response seems like structured data, trying previous: '{final_response[:50]}...'")
            
            # If the last message seems invalid, try the second-to-last
            if len(ai_messages) > 1:
                return ai_messages[-2]
            else:
                logger.warning("Only one AI message and it appears to be structured data")
                return None
        
        return final_response
    
    def _is_structured_data(self, content):
        """Check if content appears to be structured data rather than natural response"""
        content = content.strip()
        
        # Check for JSON-like structure
        if content.startswith(('{', '[')) and content.endswith(('}', ']')):
            try:
                json.loads(content)
                return True  # Valid JSON
            except json.JSONDecodeError:
                pass
        
        # Check for other structured patterns
        if (content.startswith('```') or  # Code blocks
            content.count('\n') > 10 and '"' in content and ':' in content):  # Looks like multi-line JSON
            return True
            
        return False
    
    def _sse(self, event: str, data) -> str:
        return f"data: {json.dumps({'event': event, 'data': data})}\n\n"

# App setup
agent = WorkingAgent()
app = FastAPI(title="Working Grace Papers Chat")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
async def startup():
    await agent.initialize()

@app.get("/health")
async def health():
    return {"status": "ok", "ready": agent.initialized, "tools": len(agent.tools)}

@app.post("/api/chat/start")
async def start():
    return {"session_id": agent.create_session()}

@app.post("/api/chat/stream")
async def stream(request: ChatRequest):
    return StreamingResponse(
        agent.chat(request.session_id, request.message),
        media_type="text/event-stream"
    )



if __name__ == "__main__":
    import uvicorn
    import os
    
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Starting Working Agent on port {port}")
    print(f"Demo: http://localhost:{port}/demo")
    uvicorn.run("working_agent:app", host="0.0.0.0", port=port, reload=True)