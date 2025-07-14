#!/usr/bin/env python3
"""
Clean MCP Client Example.

This is a clean implementation of an MCP client that demonstrates
all capabilities of the MCP protocol with proper error handling.
"""
import asyncio
import logging
import json
import urllib.parse
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import TextContent, TextResourceContents

# Configure logger module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Main client function that demonstrates MCP client features"""
    logger.info("Starting MCP Client")
    
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "server.py"],
    )
    
    try:
        logger.info("Connecting to MCP Server...")
        async with stdio_client(server_params) as (reader, writer):
            async with ClientSession(reader, writer) as session:
                logger.info("------------------------------------------")
                logger.info("[0] ==== Initializing session. ====")
                await session.initialize()
                
                #------------------------------------------
                # 1. Call the add tool
                logger.info("------------------------------------------")
                logger.info("[1] ==== Testing calculator tool ====")
                a = 10
                b = 20
                add_result = await session.call_tool("add", arguments={"a": a, "b": b})
                if add_result and add_result.content:
                    text_content = next((content for content in add_result.content 
                                         if isinstance(content, TextContent)), None)
                    if text_content:
                        print(f"\n1. Calculator result ({a} + {b}) = {text_content.text}")
                        
                #------------------------------------------
                # 2. Call the  completion tool
                logger.info("------------------------------------------")
                logger.info("[2] ==== Testing completion tool ====")
                completion_result = await  session.call_tool(
                    "completion",
                    arguments={
                        "model": "gpt-4",
                        "prompt": "What is the meaning of life?",
                        "temperature": 0.7,
                    }
                )
                if completion_result and completion_result.content:
                    text_content = next((content for content in completion_result.content 
                                         if isinstance(content, TextContent)), None)
                    if text_content:
                        print(f"\n2. Completion: {text_content.text}")
                        
                #------------------------------------------
                # 3. Get Models resource
                logger.info("------------------------------------------")
                logger.info("[3] ==== Testing models resource ====")
                models_response = await session.read_resource("models://")
                if models_response and models_response.contents:
                    text_resource = next((content for content in models_response.contents
                                          if isinstance(content, TextResourceContents)), None)
                    if text_resource:
                        models = json.loads(text_resource.text)
                        print(f"\n3. Available Models: {models}")
                        for model in models.get("models", []):
                            print(f"  - {model['name']} ({model['id']}): {model['description']}")
                
                #------------------------------------------
                # 4. Get Greeting resource
                logger.info("------------------------------------------")
                logger.info("[4] ==== Testing greeting resource ====")
                name = "MCP Explorer"
                encoded_name = urllib.parse.quote(name)
                greeting_response = await session.read_resource(f"greeting://{encoded_name}")
                if greeting_response and greeting_response.contents:
                    text_resource = next((content for content in greeting_response.contents
                                          if isinstance(content, TextResourceContents)), None)
                    if  text_resource:
                        print(f"\n4. Greeting: {text_resource.text}")
                
                #------------------------------------------
                # 5. Use code review prompt
                logger.info("------------------------------------------")
                logger.info("[5] ==== Testing code review prompt ====")
                sample_code = "def hello_world():\n    print('Hello, World!')"
                prompt_response = await session.get_prompt("review_code", {"code": sample_code})
                if prompt_response and prompt_response.messages:
                    message = next((msg for msg in prompt_response.messages if msg.content), None)
                    if message and message.content:
                        text_content = next((content for content in [message.content]
                                             if isinstance(content, TextContent)), None)
                        if text_content:
                            print(f"\n5. Code Review Prompt:")
                            print(f"    {text_content.text}")
                            
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
        sys.exit(1)
        
if __name__ == "__main__":
    asyncio.run(main())
