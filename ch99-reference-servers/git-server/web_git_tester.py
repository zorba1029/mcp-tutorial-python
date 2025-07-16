#!/usr/bin/env python3
"""
Git Server 웹 테스터

브라우저에서 Git server를 테스트할 수 있는 간단한 웹 인터페이스
"""

import asyncio
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import threading
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class GitServerTester:
    def __init__(self):
        self.results = []
    
    async def test_git_tool(self, tool_name, arguments):
        """Git server 도구 테스트"""
        try:
            server_params = StdioServerParameters(
                command="uv",
                args=["run", "python", "-m", "mcp_server_git", "--repository", "../.."],
                cwd="."
            )
            
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool(tool_name, arguments)
                    return {"success": True, "content": result.content[0].text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_available_tools(self):
        """사용 가능한 도구 목록 조회"""
        try:
            server_params = StdioServerParameters(
                command="uv",
                args=["run", "python", "-m", "mcp_server_git", "--repository", "../.."],
                cwd="."
            )
            
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools_result = await session.list_tools()
                    return [{"name": tool.name, "description": tool.description} for tool in tools_result.tools]
        except Exception as e:
            return []

class WebHandler(BaseHTTPRequestHandler):
    tester = GitServerTester()
    
    def do_GET(self):
        """GET 요청 처리"""
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.get_html_interface().encode())
        elif self.path == '/tools':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            # 비동기 함수를 동기적으로 실행
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            tools = loop.run_until_complete(self.tester.get_available_tools())
            loop.close()
            
            self.wfile.write(json.dumps(tools).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """POST 요청 처리 - Git 도구 실행"""
        if self.path == '/test-tool':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            
            tool_name = data.get('tool_name')
            arguments = data.get('arguments', {})
            
            # 비동기 함수를 동기적으로 실행
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.tester.test_git_tool(tool_name, arguments))
            loop.close()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def get_html_interface(self):
        """HTML 인터페이스 생성"""
        return """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Git Server 테스터</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
        .tool-box { border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }
        .result-box { background-color: #f9f9f9; border: 1px solid #ddd; padding: 10px; margin: 10px 0; border-radius: 5px; }
        .result-area {
            margin: 10px 0 20px 0;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 5px;
            border: 1px solid #e9ecef;
            min-height: 30px;
            display: none;
            font-family: monospace;
        }
        .result-area.show { display: block; }
        .result-area.loading { background: #fff3cd; border-color: #ffeaa7; }
        .result-area.success { background: #d4edda; border-color: #c3e6cb; }
        .result-area.error { background: #f8d7da; border-color: #f5c6cb; }
        button { background-color: #007bff; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; margin: 5px 0; }
        button:hover { background-color: #0056b3; }
        input, textarea { width: 100%; padding: 8px; margin: 5px 0; border: 1px solid #ddd; border-radius: 4px; }
        .success { color: green; }
        .error { color: red; }
        pre { background-color: #f8f9fa; padding: 10px; border-radius: 4px; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔧 Git Server 테스터</h1>
        <p>Git MCP Server의 도구들을 테스트할 수 있습니다.</p>
        
        <h2>📋 빠른 테스트</h2>
        <div class="tool-box">
            <h3>Git 상태 확인</h3>
            <button onclick="testToolLocal('git_status', {'repo_path': '../..'}, 'result-git-status')">Git Status 실행</button>
            <div class="result-area" id="result-git-status"></div>
        </div>
        
        <div class="tool-box">
            <h3>브랜치 목록</h3>
            <button onclick="testToolLocal('git_branch', {'repo_path': '../..', 'branch_type': 'local'}, 'result-branch-local')">로컬 브랜치</button>
            <div class="result-area" id="result-branch-local"></div>
            
            <button onclick="testToolLocal('git_branch', {'repo_path': '../..', 'branch_type': 'remote'}, 'result-branch-remote')">원격 브랜치</button>
            <div class="result-area" id="result-branch-remote"></div>
        </div>
        
        <div class="tool-box">
            <h3>커밋 히스토리</h3>
            <button onclick="testToolLocal('git_log', {'repo_path': '../..', 'max_count': 5}, 'result-log')">최근 5개 커밋</button>
            <div class="result-area" id="result-log"></div>
        </div>
        
        <div class="tool-box">
            <h3>변경사항 확인</h3>
            <button onclick="testToolLocal('git_diff_unstaged', {'repo_path': '../..', 'context_lines': 3}, 'result-diff-unstaged')">스테이징되지 않은 변경사항</button>
            <div class="result-area" id="result-diff-unstaged"></div>
            
            <button onclick="testToolLocal('git_diff_staged', {'repo_path': '../..', 'context_lines': 3}, 'result-diff-staged')">스테이징된 변경사항</button>
            <div class="result-area" id="result-diff-staged"></div>
        </div>
        
        <div class="tool-box">
            <h3>최신 커밋 상세 정보</h3>
            <button onclick="testToolLocal('git_show', {'repo_path': '../..', 'revision': 'HEAD'}, 'result-show')">HEAD 커밋 상세 정보</button>
            <div class="result-area" id="result-show"></div>
        </div>
        
        <h2>🛠️ 커스텀 테스트</h2>
        <div class="tool-box">
            <label>도구 이름:</label>
            <input type="text" id="custom-tool" placeholder="예: git_status">
            <label>인자 (JSON):</label>
            <textarea id="custom-args" rows="3" placeholder='{"repo_path": "../..", "branch_type": "local"}'></textarea>
            <button onclick="testCustomTool()">커스텀 도구 실행</button>
        </div>
        
        <h2>📊 결과</h2>
        <div id="results"></div>
    </div>

    <script>
        // 기존 전역 결과창에 표시하는 함수
        async function testTool(toolName, args) {
            const resultsDiv = document.getElementById('results');
            const timestamp = new Date().toLocaleTimeString();
            
            resultsDiv.innerHTML = `<div class="result-box"><strong>[${timestamp}] ${toolName} 실행 중...</strong></div>` + resultsDiv.innerHTML;
            
            try {
                const response = await fetch('/test-tool', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ tool_name: toolName, arguments: args })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    resultsDiv.innerHTML = `
                        <div class="result-box">
                            <strong class="success">[${timestamp}] ${toolName} ✅ 성공</strong>
                            <pre>${result.content}</pre>
                        </div>
                    ` + resultsDiv.innerHTML.replace(`<div class="result-box"><strong>[${timestamp}] ${toolName} 실행 중...</strong></div>`, '');
                } else {
                    resultsDiv.innerHTML = `
                        <div class="result-box">
                            <strong class="error">[${timestamp}] ${toolName} ❌ 실패</strong>
                            <pre>${result.error}</pre>
                        </div>
                    ` + resultsDiv.innerHTML.replace(`<div class="result-box"><strong>[${timestamp}] ${toolName} 실행 중...</strong></div>`, '');
                }
            } catch (error) {
                resultsDiv.innerHTML = `
                    <div class="result-box">
                        <strong class="error">[${timestamp}] ${toolName} ❌ 네트워크 오류</strong>
                        <pre>${error.message}</pre>
                    </div>
                ` + resultsDiv.innerHTML.replace(`<div class="result-box"><strong>[${timestamp}] ${toolName} 실행 중...</strong></div>`, '');
            }
        }
        
        // 버튼 바로 밑에 결과를 표시하는 새로운 함수
        async function testToolLocal(toolName, args, resultId) {
            const resultDiv = document.getElementById(resultId);
            const timestamp = new Date().toLocaleTimeString();
            
            // 결과창 보이기 및 로딩 상태 설정
            resultDiv.className = 'result-area show loading';
            resultDiv.innerHTML = `<strong>[${timestamp}] ${toolName} 실행 중...</strong>`;
            
            try {
                const response = await fetch('/test-tool', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ tool_name: toolName, arguments: args })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    resultDiv.className = 'result-area show success';
                    resultDiv.innerHTML = `
                        <strong>[${timestamp}] ${toolName} ✅ 성공</strong><br/>
                        <pre style="margin: 10px 0; white-space: pre-wrap;">${result.content}</pre>
                    `;
                } else {
                    resultDiv.className = 'result-area show error';
                    resultDiv.innerHTML = `
                        <strong>[${timestamp}] ${toolName} ❌ 실패</strong><br/>
                        <pre style="margin: 10px 0; white-space: pre-wrap;">${result.error}</pre>
                    `;
                }
            } catch (error) {
                resultDiv.className = 'result-area show error';
                resultDiv.innerHTML = `
                    <strong>[${timestamp}] ${toolName} ❌ 네트워크 오류</strong><br/>
                    <pre style="margin: 10px 0; white-space: pre-wrap;">${error.message}</pre>
                `;
            }
        }
        
        function testCustomTool() {
            const toolName = document.getElementById('custom-tool').value;
            const argsText = document.getElementById('custom-args').value;
            
            if (!toolName) {
                alert('도구 이름을 입력하세요.');
                return;
            }
            
            let args = {};
            if (argsText) {
                try {
                    args = JSON.parse(argsText);
                } catch (e) {
                    alert('인자 JSON 형식이 올바르지 않습니다.');
                    return;
                }
            }
            
            testTool(toolName, args);
        }
    </script>
</body>
</html>
        """

def start_web_server(port=8080):
    """웹 서버 시작"""
    server = HTTPServer(('localhost', port), WebHandler)
    print(f"🚀 Git Server 웹 테스터가 http://localhost:{port} 에서 실행 중입니다.")
    print("브라우저에서 접속하여 Git server를 테스트하세요!")
    server.serve_forever()

if __name__ == "__main__":
    start_web_server(8080) 