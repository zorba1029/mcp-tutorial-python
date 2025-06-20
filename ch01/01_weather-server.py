#!/usr/bin/env python3
from mcp.server.fastmcp import FastMCP

# Create a  FastMCP server
mcp = FastMCP(name="Weather MCP Server", version="1.0.0")

@mcp.tool()
def get_weather(location: str) -> dict:
    """Get the weather for a given location"""
    return {
        "location": location,
        "temperature": 22,
        "description": "sunny",
    }

# Alternative approach using a standalone function
@mcp.tool()
def forecast(location: str, days: int = 1) -> dict:
    """Gets weather forecast for a given location for the specified number of days."""
    # This would normally call a weather API forecast endpoint
    # Simplified for demo purposes
    return {
        "location": location,
        "forecast": [
            {"day": i+1, "temperature": 20 + i, "conditions": "Partly Cloudy"}
            for i in range(days)
        ]
    }

# Start the server using stdio transport
if __name__ == "__main__":
    mcp.run()
