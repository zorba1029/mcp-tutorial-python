from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client


# Create server parameters for stdio connection
server_params = StdioServerParameters(
    command="mcp",
    args=["run", "server.py"],
    env=None,
    name="CH03 Demo Server",
)

async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Init the connection
            await session.initialize()
            
            # List available resources
            resources = await session.list_resources()
            print("[1] LISTING RESOURCES:")
            for resource in resources:
                print(f"  Resource: {resource}")
            
            # List available tools
            tools = await session.list_tools()
            print("\n[2] LISTING TOOLS:")
            for tool in tools:
                print(f"  Tool: {tool}")
            
            # Read a resource
            print("\n[3] READING RESOURCE:")
            try:
                result = await session.read_resource("greeting://hello")
                print(f"  Resource result: {result}")
                if hasattr(result, 'contents'):
                    print(f"  Resource contents: {result.contents}")
            except Exception as e:
                print(f"  Error reading resource: {e}")
            
            # Call a tool
            result = await session.call_tool("add", arguments={"a": 1, "b": 7})
            print(f"\n[4] CALLING TOOL - <add> result: {result} (add: 1, 7)")

            # # # Call a tool with a resource
            result = await session.call_tool("get_greeting", arguments={"name": "John"})
            print(f"\n[5] CALLING TOOL - <get_greeting> result: {result}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(run())
    
#-- 실행 : stdio 서버이므로, 이 클라이언트 실행시 서버를 실행 한 후 실행 한다.
# > uv run client.py
# [06/19/25 03:07:28] INFO     Processing request of type ListResourcesRequest                                           server.py:523
# [1]Available resources:
#   Resource: ('meta', None)
#   Resource: ('nextCursor', None)
#   Resource: ('resources', [])
#                     INFO     Processing request of type ListToolsRequest                                               server.py:523

# [2] Available tools:
# Tool: ('meta', None)
# Tool: ('nextCursor', None)
# Tool: (
#     'tools', [
#         Tool(name='add', description='Add two numbers together', 
#             inputSchema={'properties': {
#                     'a': {'title': 'A', 'type': 'integer'}, 
#                     'b': {'title': 'B', 'type': 'integer'}
#                 }, 
#                 'required': ['a', 'b'], 
#                 'title': 'addArguments', 
#                 'type': 'object'
#             }, 
#             annotations=None
#         ), 
#         Tool(name='get_greeting', description='Get a personalized greeting', 
#             inputSchema={
#                 'properties': {
#                     'name': {'title': 'Name', 'type': 'string'}
#                 }, 
#                 'required': ['name'], 
#                 'title': 'get_greetingArguments', 
#                 'type': 'object'
#             }, 
#             annotations=None
#         )
#     ]
# )

# [3] Reading a resource:
#                     INFO     Processing request of type ReadResourceRequest                                            server.py:523
#   Resource result: meta=None contents=[TextResourceContents(uri=AnyUrl('greeting://hello'), mimeType='text/plain', text='Hello, hello!')]
#   Resource contents: [TextResourceContents(uri=AnyUrl('greeting://hello'), mimeType='text/plain', text='Hello, hello!')]
#                     INFO     Processing request of type CallToolRequest                                                server.py:523

# [4] Tool result: meta=None content=[TextContent(type='text', text='8', annotations=None)] isError=False (add: 1, 7)
#                     INFO     Processing request of type CallToolRequest                                                server.py:523

# [4] Tool result: [TextContent(type='text', text='Hello, John!', annotations=None)]
