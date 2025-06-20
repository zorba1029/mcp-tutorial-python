# server-fastapi.py
#
# 이 파일은 기존 server.py와 동일한 기능을 하지만,
# Starlette 대신 FastAPI 프레임워크를 사용합니다.
#
# FastAPI는 Starlette을 기반으로 만들어졌으며, 자동 API 문서,
# 데이터 유효성 검사 등 강력한 추가 기능을 제공합니다.

# 1. 라이브러리 임포트
from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP

# 2. MCP 서버 인스턴스 생성
mcp = FastMCP(name="CH03/05 FastAPI SSE Server", version="1.0.0")

# 3. FastAPI 앱 인스턴스 생성
#    FastAPI는 Starlette을 상속받으므로, 그 자체로 ASGI 애플리케이션입니다.
app = FastAPI()

# 4. FastAPI 앱에 MCP SSE 앱 마운트하기
#    FastAPI의 `mount` 메서드를 사용하여 특정 경로에 다른 ASGI 앱을 연결합니다.
#    이렇게 하면 FastAPI의 기능과 MCP의 기능을 하나의 서버에서 함께 사용할 수 있습니다.
app.mount("/", mcp.sse_app())
app.mount("/sse", mcp.sse_app())


# 5. MCP 서버 기능 추가 (기존과 동일)
@mcp.tool()
def add(a: int, b: int) -> int:
    return a + b

@mcp.tool()
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

# 6. (선택사항) FastAPI 고유의 엔드포인트 추가하기
#    이것이 FastAPI를 사용하는 큰 장점 중 하나입니다.
@app.get("/health")
def health_check():
    """FastAPI 고유의 경로: 서버의 상태를 확인하는 헬스 체크 엔드포인트"""
    return {"status": "ok", "mcp_server_name": mcp.name}


# 7. 서버 실행 (기존과 동일)
if __name__ == "__main__":
    import uvicorn
    # 실행 시 `server-fastapi:app`으로 실행해야 합니다.
    uvicorn.run("server-fastapi:app", host="0.0.0.0", port=8000, reload=True) 
    
#--------------------------------------------------------
# uv add "fastapi[all]"
# 1. MCP server 실행
# 2. Web Server 실행
# 3. CLI client test - MCP tool (add함수) 호출
#--------------------------------------------------------
#-- MCP server 실행 방법
# > uv run mcp dev server-fastapi.py
# Starting MCP inspector...
# ⚙️ Proxy server listening on 127.0.0.1:6277
# 🔑 Session token: d0c02d527d52f24c23b35d6a1cf0cef3185557cea05ffef57d251c4e0f560712
# Use this token to authenticate requests or set DANGEROUSLY_OMIT_AUTH=true to disable auth

# 🔗 Open inspector with token pre-filled:
#    http://localhost:6274/?MCP_PROXY_AUTH_TOKEN=d0c02d527d52f24c23b35d6a1cf0cef3185557cea05ffef57d251c4e0f560712
#    (Auto-open is disabled when authentication is enabled)

# 🔍 MCP Inspector is up and running at http://127.0.0.1:6274 🚀

#-- Web Server 실행 방법
# > uv run python server-fastapi.py
# INFO:     Will watch for changes in these directories: ['/Volumes/SSD_01/zorba/brain/deep-learning/microsoft-mcp-tutorial/mytrial/mcp-tutorial-python/ch03/05_sse-server']
# INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
# INFO:     Started reloader process [55556] using WatchFiles
# INFO:     Started server process [55558]
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
# [06/20/25 23:30:01] INFO     3 changes detected 

#-- CLI client test - MCP tool (add함수) 호출
# > npx @modelcontextprotocol/inspector --cli http://localhost:8000/ --method tools/call --tool-name add --tool-arg a=1 --tool-arg b=5
# {
#   "content": [
#     {
#       "type": "text",
#       "text": "6"
#     }
#   ],
#   "isError": false
# }