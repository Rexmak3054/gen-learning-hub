import os, time
import asyncio
import json
from datetime import datetime
from dotenv import load_dotenv
from contextlib import AsyncExitStack
# Add references
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import FunctionTool, MessageRole, ListSortOrder
from azure.identity import DefaultAzureCredential

# Clear the console
os.system('cls' if os.name=='nt' else 'clear')

# Load environment variables from .env file
load_dotenv()
project_endpoint = os.getenv("PROJECT_ENDPOINT")
model_deployment = os.getenv("MODEL_DEPLOYMENT_NAME")
api_key = os.getenv("MODEL_API_KEY")
# Rate limiting for Azure AI agent calls
LAST_AGENT_CALL_TIME = 0
MIN_AGENT_CALL_INTERVAL = 15  # 15 seconds between agent calls

def wait_for_agent_rate_limit():
    """Wait if necessary to respect Azure AI agent rate limits"""
    global LAST_AGENT_CALL_TIME
    current_time = time.time()
    
    if LAST_AGENT_CALL_TIME > 0:
        time_since_last = current_time - LAST_AGENT_CALL_TIME
        if time_since_last < MIN_AGENT_CALL_INTERVAL:
            wait_time = MIN_AGENT_CALL_INTERVAL - time_since_last
            print(f"⏱️ Azure AI rate limiting: waiting {wait_time:.1f} seconds...")
            time.sleep(wait_time)
    
    LAST_AGENT_CALL_TIME = time.time()

# Debug logging setup
debug_log = []

def log_debug(message, data=None):
    """Log debug information with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    log_entry = f"[{timestamp}] {message}"
    if data:
        log_entry += f"\nData: {json.dumps(data, indent=2, default=str) if isinstance(data, (dict, list)) else str(data)}"
    
    print(f"🔍 DEBUG: {log_entry}")
    debug_log.append(log_entry)
    
def save_debug_log():
    """Save debug log to logs folder with timestamp"""
    os.makedirs('logs', exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f'logs/debug_log_{timestamp}.txt'
    
    with open(log_filename, 'w') as f:
        f.write(f"Course Research Agent Debug Log\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 50 + "\n\n")
        for entry in debug_log:
            f.write(entry + '\n\n')
    print(f"\n📝 Debug log saved to {log_filename} ({len(debug_log)} entries)")

def save_tool_result(tool_name, arguments, result, call_number):
    """Save individual tool results to separate files for analysis"""
    os.makedirs('logs/tool_calls', exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'logs/tool_calls/{tool_name}_call_{call_number}_{timestamp}.json'
    
    tool_data = {
        'timestamp': datetime.now().isoformat(),
        'tool_name': tool_name,
        'call_number': call_number,
        'arguments': arguments,
        'result': result,
        'result_summary': {
            'has_error': 'error' in result if isinstance(result, dict) else False,
            'content_length': len(str(result)),
            'keys': list(result.keys()) if isinstance(result, dict) else 'Not a dict'
        }
    }
    
    with open(filename, 'w') as f:
        json.dump(tool_data, f, indent=2, default=str)
    
    print(f"  💾 Tool result saved to: {filename}")

async def connect_to_server(exit_stack: AsyncExitStack):
    server_params = StdioServerParameters(
        command="python",
        args=["course_server.py"],
        env=None
    )

    # Start the MCP server
    stdio_transport = await exit_stack.enter_async_context(stdio_client(server_params))
    stdio, write = stdio_transport
    
    # Create an MCP client session
    session = await exit_stack.enter_async_context(ClientSession(stdio, write))
    await session.initialize()
    # List available tools
    response = await session.list_tools()
    tools = response.tools
    log_debug("Connected to MCP server", {"available_tools": [tool.name for tool in tools]})
    print("\nConnected to server with tools:", [tool.name for tool in tools]) 
    return session

async def process_agent_run(agents_client, thread_id, agent_id, functions_dict):
    """Process a complete agent run with proper status monitoring"""
    
    # Create the run
    wait_for_agent_rate_limit()
    run = agents_client.runs.create(thread_id=thread_id, agent_id=agent_id)
    log_debug("🏃 Agent run created", {"run_id": run.id, "initial_status": run.status})
    
    tool_call_count = 0
    status_check_count = 0
    max_status_checks = 60  # 3 minutes timeout
    
    while status_check_count < max_status_checks:
        status_check_count += 1
        
        # Get current status
        try:
            time.sleep(3)
            run = agents_client.runs.get(thread_id=thread_id, run_id=run.id)
            log_debug(f"📊 Status check #{status_check_count}", {
                "status": run.status,
                "elapsed": f"{status_check_count * 3}s"
            })
        except Exception as e:
            if "rate_limit" in str(e).lower():
                print("⚠️ Rate limited checking status, waiting 15s...")
                time.sleep(15)
                continue
            else:
                raise
        
        # Check if run is complete
        if run.status == "completed":
            log_debug("✅ Agent run completed successfully")
            return run, True
        elif run.status == "failed":
            log_debug("❌ Agent run failed", {"error": run.last_error})
            return run, False
        elif run.status == "cancelled":
            log_debug("🚫 Agent run was cancelled")
            return run, False
        elif run.status == "requires_action":
            # Handle tool calls
            log_debug("⚙️ Processing tool calls")
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            tool_outputs = []
            
            for tool_call in tool_calls:
                tool_call_count += 1
                function_name = tool_call.function.name
                args_json = tool_call.function.arguments
                kwargs = json.loads(args_json)
                
                log_debug(f"🔧 Tool call #{tool_call_count}: {function_name}", kwargs)
                
                # Execute the tool
                required_function = functions_dict.get(function_name)
                output = await required_function(**kwargs)
                
                # Save tool result
                if hasattr(output, 'content') and output.content:
                    try:
                        result_data = json.loads(output.content[0].text)
                        save_tool_result(function_name, kwargs, result_data, tool_call_count)
                    except:
                        pass
                
                tool_outputs.append({
                    "tool_call_id": tool_call.id,
                    "output": output.content[0].text,
                })
                
                log_debug(f"✅ Tool #{tool_call_count} completed", {
                    "output_length": len(output.content[0].text)
                })
            
            # Submit tool outputs with retry
            for attempt in range(3):
                try:
                    time.sleep(2)  # Brief delay
                    agents_client.runs.submit_tool_outputs(
                        thread_id=thread_id, 
                        run_id=run.id, 
                        tool_outputs=tool_outputs
                    )
                    log_debug("📤 Tool outputs submitted successfully")
                    break
                except Exception as submit_error:
                    if "rate_limit" in str(submit_error).lower() and attempt < 2:
                        wait_time = 30 * (attempt + 1)
                        print(f"⚠️ Rate limited submitting tools, waiting {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        raise
        
        # Continue monitoring if still in progress
        elif run.status in ["queued", "in_progress"]:
            continue
        else:
            log_debug(f"🤔 Unknown status: {run.status}")
            break
    
    # Timeout handling
    if status_check_count >= max_status_checks:
        log_debug("⏱️ Agent run timed out", {"final_status": run.status})
        return run, False
    
    return run, True

async def chat_loop(session):
    # Connect to the agents client
    agents_client = AgentsClient(
        endpoint=project_endpoint,
        credential=DefaultAzureCredential(
            exclude_environment_credential=True,
            exclude_managed_identity_credential=False
        )
    )

    # List tools available on the server
    response = await session.list_tools()
    tools = response.tools

    # Build a function for each tool
    def make_tool_func(tool_name):
        async def tool_func(**kwargs):
            result = await session.call_tool(tool_name, kwargs)
            return result
        
        tool_func.__name__ = tool_name
        return tool_func

    functions_dict = {tool.name: make_tool_func(tool.name) for tool in tools}
    mcp_function_tool = FunctionTool(functions=list(functions_dict.values()))

    # Create the agent
    agent = agents_client.create_agent(
        model=model_deployment,
        name="course-research-agent",

        instructions="""You are a course research agent that helps users find suitable online learning resources.
        
        IMPORTANT TOOL USAGE:
        1. Use get_courses_info_html(platform, keywords) to search for courses:
           - platform: must be 'coursera', 'udemy', or 'edx' 
           - keywords: must be a list like ['python', 'programming'] or ['data', 'science']
        
        2. Use fetch_page_content(url) to get detailed information from specific course URLs
        
        GUIDELINES:
        - Always search for courses using the tools before making recommendations
        - Provide 3-5 specific courses with real URLs from your search results
        - Include course title, instructor/organization, platform, and direct link
        - Explain how each course matches the user's needs
        - If you need more details about a specific course, use fetch_page_content with the course URL
        
        NEVER recommend courses that you haven't found through the tools.
        """,
        tools=mcp_function_tool.definitions
    )
    
    # Enable auto function calling
    agents_client.enable_auto_function_calls(tools=mcp_function_tool)

    # Create a thread for the chat session
    thread = agents_client.threads.create()
    session_id = thread.id[:8]
    log_debug("📄 Created chat thread", {"thread_id": thread.id, "session_id": session_id})

    while True:
        user_input = input("Describe your role and skills that you are looking to learn. Use 'quit' to exit.\nUSER: ").strip()
        if user_input.lower() == "quit":
            print("Exiting chat.")
            save_debug_log()
            break
        
        if not user_input:
            print("Please enter a non-empty message.")
            continue

        log_debug("💬 USER INPUT", {"message": user_input})

        try:
            # Create user message
            agents_client.messages.create(
                thread_id=thread.id,
                role=MessageRole.USER,
                content=user_input,
            )
            
            # Process the agent run
            run, success = await process_agent_run(agents_client, thread.id, agent.id, functions_dict)
            
            if not success:
                if run and run.status == "failed":
                    error_str = str(run.last_error) if run.last_error else ""
                    if "rate_limit_exceeded" in error_str:
                        import re
                        wait_match = re.search(r'(\d+) seconds', error_str)
                        wait_time = int(wait_match.group(1)) if wait_match else 60
                        print(f"⚠️ Rate limited. Automatically retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        
                        # Retry once
                        retry_run, retry_success = await process_agent_run(agents_client, thread.id, agent.id, functions_dict)
                        if not retry_success:
                            print("❌ Retry also failed. Please try a simpler question.")
                            continue
                        run = retry_run
                    else:
                        print(f"❌ Run failed: {run.last_error}")
                        continue
                else:
                    print("❌ Agent run timed out or failed to start.")
                    continue

            # Get and display response
            messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
            messages_list = list(messages)
            
            log_debug("📬 Processing agent response", {"total_messages": len(messages_list)})
            
            # Find the latest assistant response
            latest_assistant_response = None
            for message in reversed(messages_list):  # Check from most recent
                if message.role == MessageRole.ASSISTANT and message.text_messages:
                    latest_assistant_response = message.text_messages[-1].text.value
                    break
            
            if latest_assistant_response:
                print(f"\nASSISTANT:\n{latest_assistant_response}\n")
                log_debug("🤖 AGENT RESPONSE", {
                    "content_length": len(latest_assistant_response),
                    "content": latest_assistant_response
                })
                
                # Save response
                os.makedirs('logs/agent_responses', exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f'logs/agent_responses/response_{session_id}_{timestamp}.json'
                
                response_data = {
                    'timestamp': datetime.now().isoformat(),
                    'user_query': user_input,
                    'agent_response': latest_assistant_response,
                    'contains_urls': 'http' in latest_assistant_response.lower()
                }
                
                with open(filename, 'w') as f:
                    json.dump(response_data, f, indent=2)
                print(f"💾 Response saved to: {filename}")
            else:
                print("❌ No assistant response found")
                log_debug("❌ No assistant response found in messages")

        except Exception as e:
            log_debug("❌ ERROR in chat loop", {
                "error_type": type(e).__name__,
                "error_message": str(e)
            })
            print(f"❌ Error: {e}")
            
            if "rate_limit" in str(e).lower():
                print("💡 Rate limit detected. Please wait 60 seconds before trying again.")

    # Cleanup
    log_debug("🗑️ Cleaning up agent")
    agents_client.delete_agent(agent.id)
    save_debug_log()

async def main():
    exit_stack = AsyncExitStack()
    try:
        session = await connect_to_server(exit_stack)
        await chat_loop(session)
    finally:
        await exit_stack.aclose()

if __name__ == "__main__":
    asyncio.run(main())
