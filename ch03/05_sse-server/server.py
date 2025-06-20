#
# SSE 서버 (Server-Sent Event)
#----------------------------
# -- 서버-클라이언트 스트리밍 표준으로, 서버가 HTTP를 통해 클라이언트에 실시간 업데이트를 
#    푸시할 수 있도록 합니다. 이는 채팅 애플리케이션, 알림 또는 실시간 데이터 피드와 같이 실시간 
#    업데이트가 필요한 애플리케이션에 특히 유용합니다. 또한, 예를 들어 클라우드에서 실행되는 서버에 
#    서버를 설치하면 여러 클라이언트가 동시에 서버를 사용할 수 있습니다.

# 학습 목표
# -- 이 수업을 마치면 다음을 수행할 수 있습니다.
# - SSE 서버를 구축합니다.
# - Inspector를 사용하여 SSE 서버를 디버깅합니다.
# - Visual Studio Code를 사용하여 SSE 서버를 사용합니다.

# 준비사항
# - 터미널 화면
# - Visual Studio Code
# - Inspector

# 1. 서버 instance 생성
from starlette.applications import Starlette
from starlette.routing import Mount, Host
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="CH03/05 SSE Server", version="1.0.0")

# 2. 서버 라우팅 설정
# Mount the SSE server to the UvicornWeb (ASGI) server
# Create an instance of an ASGI server (using Starletter specifically) and mount the default route /
# What happens behind the scenes is that the routes /sse and /messages are setup to handle 
# connections and messages respectively. The rest of the app, like adding features like tools, 
# happens like with stdio servers.
#  That ends up mounting an /sse and /messages route on the app instance.
app = Starlette(
    routes=[
        Mount("/", app=mcp.sse_app()),
        Mount("/sse", app=mcp.sse_app()),
    ]
)

# 3. 서버 기능 추가
@mcp.tool()
def add(a: int, b: int) -> int:
    return a + b

@mcp.tool()
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

# # 4. 서버 실행
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

#----------------------------------------
# 1] 실행 - uvicor web server로
# > uv run server.py
# INFO:     Started server process [16776]
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
# INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
# INFO:     127.0.0.1:51638 - "GET /sse HTTP/1.1" 200 OK
# INFO:     127.0.0.1:51640 - "POST /messages/?session_id=e58b87b24171407daf7235a15fee1175 HTTP/1.1" 202 Accepted
# INFO:     127.0.0.1:51640 - "POST /messages/?session_id=e58b87b24171407daf7235a15fee1175 HTTP/1.1" 202 Accepted
# INFO:     127.0.0.1:51642 - "POST /messages/?session_id=e58b87b24171407daf7235a15fee1175 HTTP/1.1" 202 Accepted
# [06/19/25 23:08:11] INFO     Processing request of type ListToolsRequest 
# INFO:     127.0.0.1:51876 - "GET /sse HTTP/1.1" 200 OK
# INFO:     127.0.0.1:51878 - "POST /messages/?session_id=abdf4c86cad24c329502032210aa6fbe HTTP/1.1" 202 Accepted
# INFO:     127.0.0.1:51878 - "POST /messages/?session_id=abdf4c86cad24c329502032210aa6fbe HTTP/1.1" 202 Accepted
# INFO:     127.0.0.1:51880 - "POST /messages/?session_id=abdf4c86cad24c329502032210aa6fbe HTTP/1.1" 202 Accepted
# [06/19/25 23:16:04] INFO     Processing request of type ListResourceTemplatesRequest  
#----------------------------------------
#--- CLI client test:
# > npx @modelcontextprotocol/inspector --cli http://localhost:8000/sse --method tools/list
# {
#   "tools": [
#     {
#       "name": "add",
#       "description": "",
#       "inputSchema": {
#         "type": "object",
#         "properties": {
#           "a": {
#             "title": "A",
#             "type": "integer"
#           },
#           "b": {
#             "title": "B",
#             "type": "integer"
#           }
#         },
#         "required": [
#           "a",
#           "b"
#         ],
#         "title": "addArguments"
#       }
#     },
#     {
#       "name": "get_greeting",
#       "description": "Get a personalized greeting",
#       "inputSchema": {
#         "type": "object",
#         "properties": {
#           "name": {
#             "title": "Name",
#             "type": "string"
#           }
#         },
#         "required": [
#           "name"
#         ],
#         "title": "get_greetingArguments"
#       }
#     }
#   ]
# }
#----------------------------
# > npx @modelcontextprotocol/inspector --cli http://localhost:8000/messages --method resources/templates/list
# {
#   "resourceTemplates": [
#     {
#       "uriTemplate": "greeting://{name}",
#       "name": "get_greeting",
#       "description": "Get a personalized greeting"
#     }
#   ]
# }

   
#----------------------------------------
# 2] 실행 - mcp server로 
# > uv run mcp dev server.py
# Starting MCP inspector...
# ⚙️ Proxy server listening on 127.0.0.1:6277
# 🔑 Session token: 53dc78f5ef3aae42d76243ca70ef7ea254340f3224041e3b3bd17cfc1c1fbe44
# Use this token to authenticate requests or set DANGEROUSLY_OMIT_AUTH=true to disable auth

# 🔗 Open inspector with token pre-filled:
#    http://localhost:6274/?MCP_PROXY_AUTH_TOKEN=53dc78f5ef3aae42d76243ca70ef7ea254340f3224041e3b3bd17cfc1c1fbe44
#    (Auto-open is disabled when authentication is enabled)

# 🔍 MCP Inspector is up and running at http://127.0.0.1:6274 🚀
# New STDIO connection request
#--- 테스트는 웹 브라우저 inspector에서
#    http://localhost:6274/?MCP_PROXY_AUTH_TOKEN=53dc78f5ef3aae42d76243ca70ef7ea254340f3224041e3b3bd17cfc1c1fbe44
#    (Auto-open is disabled when authentication is enabled)
#    에서 합니다.


#----------------------------------------
# 3] CLI 에서 tool 실행 - add()
# -- 즉, 웹서버 (Uvicorn)이 요청을 받아서, 해당 tool - add()를 실행하고, 결과를 반환합니다.
# > npx @modelcontextprotocol/inspector --cli http://localhost:8000/sse --method tools/call --tool-name add --tool-arg a=1 --tool-arg b=2
# {
#   "content": [
#     {
#       "type": "text",
#       "text": "3"
#     }
#   ],
#   "isError": false
# }