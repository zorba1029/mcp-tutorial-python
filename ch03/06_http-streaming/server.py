#
# HTTP Streaming 서버 구현
#
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, HTMLResponse
from mcp.server.fastmcp import FastMCP, Context
from mcp.types import TextContent
import asyncio
import uvicorn
import os

# Create an MCP Server
mcp = FastMCP(name="http-streaming-server")

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def root():
    html_path = os.path.join(os.path.dirname(__file__), "welcome.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

async def event_stream(message: str):
    for i in range(1, 4):
        yield f"Processing file {i}/3...\n"
        await asyncio.sleep(1)
    yield f"Here's the file content: {message}\n"

@app.get("/stream")
async def stream(message: str = "hello"):
    return StreamingResponse(event_stream(message), media_type="text/event-stream")

@mcp.tool(description="A tool that simulates file processing and sends progress notifications")
async def process_file(message: str, ctx: Context) -> TextContent:
    files = [f"file_{i}.txt" for i in range(1, 4)]
    for idx, file in enumerate(files):
        await ctx.info(f"Processing {file} ({idx}/{len(files)})...")
        await asyncio.sleep(1)
    await ctx.info(f"All files processed")
    return TextContent(type="text", text=f"Processed files: {', '.join(files)} | Messages: {message}")

if __name__ == "__main__":
    import sys
    if "mcp" in sys.argv:
        # Configure MCP server with streamable-http transport
        print("Starting MCP Server wiht streamable-http transport...")
        # MCP server will create its own FastAPI app with the /mcp endpoint
        mcp.run(transport="streamable-http")
    else:
        # Start FastAPI app for classic HTTP Streaming
        print("Starting FastAPI server for classic HTTP Streaming...")
        uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)

#--실행 방법
# 1. MCP server mode
# > uv run mcp dev server.py mcp
# 2. Classic HTTP streaming server mode
# > uv run server.py

#-- 출력 결과
#---------------------------------------------
# 1. MCP server mode
# > uv run server.py mcp
# Starting MCP Server wiht streamable-http transport...
# INFO:     Started server process [36465]
# INFO:     Waiting for application startup.
# [06/21/25 01:02:15] INFO     StreamableHTTP session manager started               streamable_http_manager.py:109
# INFO:     Application startup complete.
# INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)

#--- >> response to client request <<---------------
# //////////
# INFO:     127.0.0.1:59014 - "POST /mcp HTTP/1.1" 307 Temporary Redirect
# [06/21/25 01:16:49] INFO     Created new transport with session ID:               streamable_http_manager.py:224
#                              0208b7d57f024bba93722a0dd631b765                                                   
# INFO:     127.0.0.1:59014 - "POST /mcp/ HTTP/1.1" 200 OK
# INFO:     127.0.0.1:59017 - "GET /mcp HTTP/1.1" 307 Temporary Redirect
# INFO:     127.0.0.1:59018 - "POST /mcp HTTP/1.1" 307 Temporary Redirect
# INFO:     127.0.0.1:59017 - "GET /mcp/ HTTP/1.1" 200 OK
# INFO:     127.0.0.1:59018 - "POST /mcp/ HTTP/1.1" 202 Accepted
# INFO:     127.0.0.1:59020 - "POST /mcp HTTP/1.1" 307 Temporary Redirect
# INFO:     127.0.0.1:59020 - "POST /mcp/ HTTP/1.1" 200 OK
#                     INFO     Processing request of type CallToolRequest                            server.py:523
# INFO:     127.0.0.1:59024 - "DELETE /mcp HTTP/1.1" 307 Temporary Redirect
# [06/21/25 01:16:52] INFO     Terminating session: 0208b7d57f024bba93722a0dd631b765        streamable_http.py:614
# INFO:     127.0.0.1:59024 - "DELETE /mcp/ HTTP/1.1" 200 OK

#---------------------------------------------
# 2. Classic HTTP streaming server mode
# > uv run server.py
# Starting FastAPI server for classic HTTP Streaming...
# INFO:     Will watch for changes in these directories: ['/Volumes/SSD_01/zorba/brain/deep-learning/microsoft-mcp-tutorial/mytrial/mcp-tutorial-python/ch03/06_http-streaming']
# INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
# INFO:     Started reloader process [33796] using WatchFiles
# INFO:     Started server process [33811]
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.

# -- >> response to client request <<---------------
# INFO:     127.0.0.1:58288 - "GET /stream?message=hello HTTP/1.1" 200 OK

