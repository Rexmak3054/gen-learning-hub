from typing import Annotated
import asyncio

from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition

import os
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.chat_models import init_chat_model

from dotenv import load_dotenv

load_dotenv()

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

# Enable LangGraph debugging (optional)
# os.environ["LANGCHAIN_TRACING_V2"] = "true"
# os.environ["LANGCHAIN_PROJECT"] = "course-research-debug"

async def main():
    # Initialize MCP client
    client = MultiServerMCPClient(
        {
            "course": {
                "command": "python",
                # Make sure to update to the full absolute path to your course_server.py file
                "args": ["course_server.py"],
                "transport": "stdio",
            },
        }
    )
    
    # Get tools from MCP server
    tools = await client.get_tools()
    print(f"✅ Loaded {len(tools)} tools from MCP server")
    for tool in tools:
        print(f"  - {tool.name}")
    
    # Initialize the language model
    llm = init_chat_model("openai:gpt-4o")
    
    # System message to encourage tool use
    system_message = """You are a helpful course research assistant. You have access to tools that can search for courses on Coursera, Udemy, and edX.
    
    IMPORTANT: Always use the available tools to search for actual courses before responding. Never provide generic responses without using the tools first.
    
    The advise you give should include what the user is going to learn from this course and how they can apply the skills to their role.
    Also, structure your response to include the course key details. 
    """
    
    # Define the chatbot function
    def chatbot(state: MessagesState):
        # Add system message if this is the first interaction
        messages = state["messages"]
        if not any(hasattr(msg, 'type') and msg.type == "system" for msg in messages):
            messages = [SystemMessage(content=system_message)] + messages
        
        return {"messages": [llm.bind_tools(tools).invoke(messages)]}
    
    # Build the graph using MessagesState
    graph_builder = StateGraph(MessagesState)
    
    # Add nodes - using standard ToolNode (you'll make server async)
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_node("tools", ToolNode(tools))
    
    # Add edges
    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_conditional_edges(
        "chatbot",
        tools_condition,
    )
    graph_builder.add_edge("tools", "chatbot")
    
    # Compile the graph
    graph = graph_builder.compile()
    
    print("\n🚀 Course Research Agent with LangGraph Ready!")
    print("Ask me to help you find courses on Coursera, Udemy, or edX")
    print("Type 'quit', 'exit', or 'q' to end the conversation\n")
    
    # Initialize conversation state
    conversation_state = {"messages": []}
    
    # Main chat loop
    while True:
        try:
            user_input = input("User: ").strip()
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break
            
            if not user_input:
                print("Please enter a message.")
                continue
            
            # Add the new user message and invoke graph
            conversation_state = await graph.ainvoke({
                "messages": conversation_state["messages"] + [HumanMessage(content=user_input)]
            })
            
            # Get the latest assistant message and display it
            if conversation_state["messages"]:
                latest_message = conversation_state["messages"][-1]
                if hasattr(latest_message, 'content'):
                    print(f"Assistant: {latest_message.content}")
                else:
                    print("Assistant: [Response received but no content]")
            
            print()  # Add spacing after response
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Please try again.")

if __name__ == "__main__":
    asyncio.run(main())
