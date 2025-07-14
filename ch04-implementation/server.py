#!/usr/bin/env python3
"""
Model Context Protocol (MCP) Python Sample Implementation.

This module demonstrates how to implement a basic MCP server that can handle
completion requests. It provides a mock implementation that simulates
interaction with various AI models.

For more information about MCP: https://modelcontextprotocol.io/
"""
import json
import logging
from mcp.server.fastmcp import FastMCP

# Configure logger module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define available models
AVAILABLE_MODELS = ["gpt-4", "llama-3-70b", "claude-3-sonnet"]

# Create an MCP Server
mcp = FastMCP("CH)$ Python MCP Server")

# Define a Tool for generating completions
@mcp.tool()
def completion(model: str, prompt: str, temperature: float = 0.7, max_tokens: int = 100) -> str:
    """
    Generate completions using AI models

    Args:
        model (str): The AI model to use for completion
        prompt (str): The prompt text to use for completion
        temperature (float, optional): The temperature (0.0 to 1.0).
        max_tokens (int, optional): The maximum number of tokens to generate.
    """
    # Validate model
    if model not in AVAILABLE_MODELS:
        raise ValueError(f"Model {model} not supported.")
    
    # In a real implementation, this would call an AI model
    # Here we porvide a more comprehensive mock response based on the prompt
    logging.info(f"Processing completions request for model: {model} with temperature: {temperature}")
    
    # Return different responses based on common prommpt
    if "meaning of life" in prompt.lower():
        completion_text = """The meaning of life is a philosophical question that has been debated 
        throughout human history. According to Douglas Adams in 'The Hitchhiker's Guide to the Galaxy', 
        the answer is simply '42'. However, many philosophers suggest that the meaning of life is 
        something each person must discover for themselves through their own experiences, values, 
        and beliefs."""
    elif "hello" in prompt.lower() or "hi" in prompt.lower():
        completion_text = """Hello! I'm a simulated AI response from the MCP server example. How can 
        I help you today?"""
    elif "who are you" in prompt.lower():
        completion_text = f"""I'm a mock {model} model response from the Model Context Protocol (MCP) 
        Python sample implementation. I'm not actually using {model}, just simulating how it would respond
        in a real MCP server."""
    else:
        completion_text = f"""This is a simulated response to your prompt about '{prompt[:30]}...' 
        from model {model}. In a real implementation, you would get an actual AI-generated 
        completion here."""
    
    # Return the response
    return completion_text

# Define a Calculator tool to add two numbers
@mcp.tool()
def add(a: int, b: int) -> int:
    logger.info(f"Adding {a} and {b}")
    return a + b

# Define a Resource to expose  available AI models
@mcp.resource("models://")
def get_models() -> str:
    """ Get information about available AI models"""
    logger.info("Retrieving available AI models")
    models_data = [
        { 
            "id": "gpt-4",
            "name": "GPT-4",
            "description": "OpenAI's GPT-4 large language model"
        },
        {
            "id": "llama-3-70b",
            "name": "LLaMA 3 (70B)",
            "description": "Meta's LLaMA 3 with 70 billion parameters"
        },
        {
            "id": "claude-3-sonnet",
            "name": "Claude 3 Sonnet",
            "description": "Anthropic's Claude 3 Sonnet model"
        }
    ]
    return json.dumps({"models": models_data})

# Define a greeting Resource that dynamically constructs a personalized greeting
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Return a greeting for the given name"""
    import urllib.parse
    # Decode URL-encoded name
    decoded_name = urllib.parse.unquote(name)
    logger.info(f"Generating greeting for {decoded_name}")
    return f"Hello, {decoded_name}!"

# Define a prompt for code review
@mcp.prompt()
def review_code(code: str) -> str:
    """Provide a template for reviewing code
    Returns:
        A prompt that asks the LLM to review the code
    """
    logger.info(f"Creating code review prompt for  {len(code)} bytes of code")
    return f"""Please review this ocde and provide feedback on best practices, potential bugs, 
and improvements:\n\n```\n{code}\n```"""

if __name__ == "__main__":
    logger.info(f"MCP Server initialized")
    logger.info(f"Supported models: {', '.join(AVAILABLE_MODELS)}")
    
    # Run the  server with stdio transport
    # This  can be tested with one of these methods:
    # 1. Direct execution: python server.py
    # 2. MCP inspector: mcp sev server.py
    # 3. Install in Claude Desktop: mcp install server.py
    mcp.run()
