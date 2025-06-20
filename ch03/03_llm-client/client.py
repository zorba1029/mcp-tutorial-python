from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

# LLM
import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
import json
from dotenv import load_dotenv

load_dotenv()

# Create server parameters for stdio connection
server_params = StdioServerParameters(
    command="mcp",
    args=["run", "server.py"],
    env=None,
    name="CH03/03 LLM MCP Server",
)

#---------------------------------
def  convert_to_llm_tool(tool):
    # print(f"TOOL: {tool}")
    tool_schema = {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "type": "function",
            "parameters": {
                "type": "object",
                "properties": tool.inputSchema["properties"],
            }
        }
    }
    
    return tool_schema

# LLM -----------------------------
def call_llm(prompt, functions):
    token = os.environ["GITHUB_TOKEN"]
    endpoint = "https://models.inference.ai.azure.com"
    model_name = "gpt-4o"
    
    client = ChatCompletionsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(token),
    )
    
    response = client.complete(
        messages=[
            { "role": "system", "content": "You are a helpful assistant."},
            { "role": "user", "content": prompt},
        ],
        model=model_name,
        tools=functions,
        # Optional parameters
        temperature=1.0,
        max_tokens=1000,
        top_p=1.0,
    )
    
    response_message = response.choices[0].message
    
    functions_to_call = []
    if response_message.tool_calls:
        for tool_call in response_message.tool_calls:
            print(f"TOOL CALL: {tool_call}")
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            functions_to_call.append({"name": name, "arguments": args})
    
    return functions_to_call

#---------------------------------
async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Init the connection
            await session.initialize()
            
            # List available resources
            resources = await session.list_resources()
            print("[1] LISTING RESOURCES: --------------------------------")
            for i, resource in enumerate(resources):
                print(f"<{i}> Resource: {resource}")
            
            # List available tools
            tools_response = await session.list_tools()
            print("\n[2] LISTING TOOLS: --------------------------------")
            functions = []
            
            # Iterate over the actual list of tools inside the response
            for i, tool in enumerate(tools_response.tools):
                print(f"<{i}> Tool Name: {tool.name}")
                print(f"    Tool Description: {tool.description}")
                print(f"    Tool Schema Properties: {tool.inputSchema['properties']}\n") 
                functions.append(convert_to_llm_tool(tool))
            
            prompt = "Add 2 to 20"
            
            # ask LLM what tools to all, if any
            print("\n[3] CALLING LLM --------------------------------")
            functions_to_call = call_llm(prompt, functions)
            
            # call suggested functions
            print("\n[4] CALLING TOOLS --------------------------------")
            for i, fn in enumerate(functions_to_call):
                print(f"<{i}> CALLING TOOL: {fn}")
                result = await session.call_tool(fn["name"], arguments=fn["arguments"])
                print(f"    TOOLS RESULT: {result.content}\n")
            
            # # Read a resource
            # print("\n[3] READING RESOURCE:")
            # try:
            #     result = await session.read_resource("greeting://hello")
            #     print(f"  Resource result: {result}")
            #     if hasattr(result, 'contents'):
            #         print(f"  Resource contents: {result.contents}")
            # except Exception as e:
            #     print(f"  Error reading resource: {e}")
            
            # # Call a tool
            # result = await session.call_tool("add", arguments={"a": 1, "b": 7})
            # print(f"\n[4] CALLING TOOL - <add> result: {result} (add: 1, 7)")

            # # # # Call a tool with a resource
            # result = await session.call_tool("get_greeting", arguments={"name": "John"})
            # print(f"\n[5] CALLING TOOL - <get_greeting> result: {result}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(run())
    
#---------------------------------
# > uv run client.py
# [06/19/25 18:32:57] INFO     Processing request of type ListResourcesRequest                       server.py:523
# [1] LISTING RESOURCES:--------------------------------
# <0> Resource: ('meta', None)
# <1> Resource: ('nextCursor', None)
# <2> Resource: ('resources', [])
#                     INFO     Processing request of type ListToolsRequest                           server.py:523

# [2] LISTING TOOLS:
# <0> Tool Name: add
#     Tool Description: Add two numbers together
#     Tool Schema Properties: {
#       'a': {'title': 'A', 'type': 'integer'}, 
#       'b': {'title': 'B', 'type': 'integer'}
#     }

# <1> Tool Name: get_greeting
#     Tool Description: Get a personalized greeting
#     Tool Schema Properties: {'name': {'title': 'Name', 'type': 'string'}}

# [3] CALLING LLM --------------------------------
# TOOL CALL: {
#     'function': {
#         'arguments': '{"a":2,"b":20}', 
#         'name': 'add'
#     }
#     'id': 'call_ZvZCw6e4M7JIwrx5EEA43Orv', 
#     'type': 'function'
# }

# [4] CALLING TOOLS --------------------------------
# <0> CALLING TOOL: {'name': 'add', 'arguments': {'a': 2, 'b': 20}}
# [06/19/25 18:33:01] INFO     Processing request of type CallToolRequest                            server.py:523
#     TOOLS RESULT: [TextContent(type='text', text='22', annotations=None)]
    
    
