# server.py
from mcp.server.fastmcp import FastMCP

# create a FastMCP server
mcp = FastMCP(name="CH03 Demo Server", version="1.0.0")

# define a tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b

# define a function that is BOTH a resource and a tool
@mcp.tool()
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

# Start the server
if __name__ == "__main__":
    mcp.run()

#-- mcp inspector 실행 --
# > uv run mcp dev server.py
# Need to install the following packages:
# @modelcontextprotocol/inspector@0.14.3
# Ok to proceed? (y) y

# Starting MCP inspector...
# ⚙️ Proxy server listening on 127.0.0.1:6277
# 🔑 Session token: a5d3992192c1bc23d009bf6dbc8470f7b816e654a47a31b64aa09923d7858c6f
# Use this token to authenticate requests or set DANGEROUSLY_OMIT_AUTH=true to disable auth

# 🔗 Open inspector with token pre-filled:
#    http://localhost:6274/?MCP_PROXY_AUTH_TOKEN=a5d3992192c1bc23d009bf6dbc8470f7b816e654a47a31b64aa09923d7858c6f
#    (Auto-open is disabled when authentication is enabled)

# 🔍 MCP Inspector is up and running at http://127.0.0.1:6274 🚀
# http://localhost:6274/?MCP_PROXY_AUTH_TOKEN=a5d3992192c1bc23d009bf6dbc8470f7b816e654a47a31b64aa09923d7858c6f

