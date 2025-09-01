#!/usr/bin/env python3
"""
Debug why agent isn't generating responses
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def debug_agent_execution():
    """Test agent execution step by step"""
    
    print("🔍 Debug Agent Execution")
    print("=" * 40)
    
    try:
        # Test basic imports
        print("1. Testing imports...")
        from langchain_core.messages import HumanMessage, SystemMessage
        from langchain.chat_models import init_chat_model
        from langgraph.graph import StateGraph, START, MessagesState
        from langgraph.prebuilt import ToolNode, tools_condition
        from langchain_mcp_adapters.client import MultiServerMCPClient
        print("   ✅ All imports successful")
        
        # Test MCP client
        print("\\n2. Testing MCP client...")
        course_server_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "course_server.py")
        print(f"   Course server path: {course_server_path}")
        print(f"   File exists: {os.path.exists(course_server_path)}")
        
        client = MultiServerMCPClient({
            "course": {
                "command": "python",
                "args": [course_server_path],
                "transport": "stdio",
            }
        })
        
        tools = await client.get_tools()
        print(f"   ✅ MCP tools loaded: {len(tools)}")
        for tool in tools:
            print(f"      - {tool.name}")
        
        # Test LLM
        print("\\n3. Testing LLM...")
        llm = init_chat_model("openai:gpt-4o")
        print("   ✅ LLM initialized")
        
        # Test simple LLM call without tools
        print("\\n4. Testing simple LLM call...")
        simple_messages = [
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content="Hello!")
        ]
        
        try:
            simple_response = llm.invoke(simple_messages)
            print(f"   ✅ Simple LLM response: '{simple_response.content[:60]}...'")
        except Exception as e:
            print(f"   ❌ Simple LLM failed: {e}")
            return
        
        # Test LLM with tools
        print("\\n5. Testing LLM with tools...")
        try:
            llm_with_tools = llm.bind_tools(tools)
            tool_response = llm_with_tools.invoke(simple_messages)
            print(f"   ✅ LLM with tools response: '{tool_response.content[:60]}...'")
        except Exception as e:
            print(f"   ❌ LLM with tools failed: {e}")
            return
        
        # Test graph building
        print("\\n6. Testing graph...")
        def chatbot(state):
            return {"messages": [llm.bind_tools(tools).invoke(state["messages"])]}
        
        graph_builder = StateGraph(MessagesState)
        graph_builder.add_node("chatbot", chatbot)
        graph_builder.add_node("tools", ToolNode(tools))
        graph_builder.add_edge(START, "chatbot")
        graph_builder.add_conditional_edges("chatbot", tools_condition)
        graph_builder.add_edge("tools", "chatbot")
        
        graph = graph_builder.compile()
        print("   ✅ Graph compiled successfully")
        
        # Test graph execution
        print("\\n7. Testing graph execution...")
        test_messages = [
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content="Hello!")
        ]
        
        try:
            graph_result = await graph.ainvoke({"messages": test_messages})
            print(f"   ✅ Graph executed successfully")
            print(f"   Result type: {type(graph_result)}")
            print(f"   Result keys: {graph_result.keys() if graph_result else 'None'}")
            
            if graph_result and "messages" in graph_result:
                messages = graph_result["messages"]
                print(f"   Messages in result: {len(messages)}")
                
                for i, msg in enumerate(messages):
                    print(f"      Message {i}: {type(msg).__name__}")
                    if hasattr(msg, 'content'):
                        print(f"         Content: '{msg.content[:50]}...'")
                    if hasattr(msg, 'tool_calls'):
                        print(f"         Tool calls: {len(msg.tool_calls) if msg.tool_calls else 0}")
        except Exception as e:
            print(f"   ❌ Graph execution failed: {e}")
            import traceback
            traceback.print_exc()
            return
        
        print("\\n✅ All components working! Agent should be functional.")
        
        # Test with course request
        print("\\n8. Testing course request...")
        course_messages = [
            SystemMessage(content="You are a helpful assistant. Use course tools when users ask about learning."),
            HumanMessage(content="I want to learn Python programming")
        ]
        
        try:
            course_result = await graph.ainvoke({"messages": course_messages})
            print(f"   ✅ Course request processed")
            
            if course_result and "messages" in course_result:
                for i, msg in enumerate(course_result["messages"]):
                    if hasattr(msg, 'content') and msg.content:
                        content = msg.content
                        if '"courses"' in content:
                            print(f"   📚 Found course data in message {i}")
                        else:
                            print(f"   💬 Message {i}: '{content[:50]}...'")
        except Exception as e:
            print(f"   ❌ Course request failed: {e}")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔍 This will test each component step by step")
    print("to find where the agent execution is failing.")
    print()
    
    asyncio.run(debug_agent_execution())
