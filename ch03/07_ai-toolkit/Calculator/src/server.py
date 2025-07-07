"""
Sample MCP Calculator Server implementation in Python.

This module demonstrates how to create a simple MCP server with calculator tools
that can perform basic arithmetic operations (add, subtract, multiply, divide).
-- July 7, 2025
-- MCP server 생성하기
"""
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
server = FastMCP("calculator")

@server.tool()
async def add(a: float, b: float) -> float:
    """Add two numbers together and return the result."""
    return a + b

@server.tool()
async def subtract(a: float, b: float) -> float:    
    """Subtract b from a and return the result."""
    return a - b

@server.tool()
async def multiply(a: float, b: float) -> float:
    """Multiply two numbers together and return the result."""
    return a * b

@server.tool()
async def divide(a: float, b: float) -> float:
    """Divide a by b and return the result.
    
    Raises:
        ValueError: If b is zero
    """
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b
