#!/usr/bin/env python3
"""
Git Server 테스트 클라이언트

사용법:
1. 터미널 1에서: python -m mcp_server_git --repository .
2. 터미널 2에서: python test_git_client.py
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import subprocess
import sys

async def test_git_server():
    # git server 프로세스 시작 - 상위 디렉토리를 repository로 설정
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "python", "-m", "mcp_server_git", "--repository", "../.."],
        cwd="."
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 서버 초기화
            await session.initialize()
            
            print("🔧 Git Server 테스트 시작")
            print("=" * 50)
            
            # 1. 도구 목록 확인
            tools_result = await session.list_tools()
            print("📋 사용 가능한 도구들: \n\tsession_list_tools()")
            for tool in tools_result.tools:
                print(f"  - {tool.name}: {tool.description}")
            print()
            
            # 2. Git 상태 확인
            print("📊 Git 상태: \n\tsession.call_tool('git_status', {'repo_path': '../..'})")
            try:
                result = await session.call_tool("git_status", {
                    "repo_path": "../.."
                })
                print(f"  {result.content[0].text}")
            except Exception as e:
                print(f"  ❌ 오류: {e}")
            print()
            
            # 3. 브랜치 목록 확인
            print("🌳 로컬 브랜치 목록: \n\tsession.call_tool('git_branch', {'repo_path': '../..', 'branch_type': 'local'})")
            try:
                result = await session.call_tool("git_branch", {
                    "repo_path": "../..",
                    "branch_type": "local"
                })
                print(f"  {result.content[0].text}")
            except Exception as e:
                print(f"  ❌ 오류: {e}")
            print()
            
            # 4. 커밋 히스토리 확인 (최근 5개)
            print("📜 최근 커밋 히스토리 (5개): \n\tsession.call_tool('git_log', {'repo_path': '../..', 'max_count': 5})")
            try:
                result = await session.call_tool("git_log", {
                    "repo_path": "../..",
                    "max_count": 5
                })
                print(f"  {result.content[0].text}")
            except Exception as e:
                print(f"  ❌ 오류: {e}")
            print()
            
            # 5. 스테이징되지 않은 변경사항 확인
            print("🔍 스테이징되지 않은 변경사항: \n\tsession.call_tool('git_diff_unstaged', {'repo_path': '../..', 'context_lines': 3})")
            try:
                result = await session.call_tool("git_diff_unstaged", {
                    "repo_path": "../..",
                    "context_lines": 3
                })
                content = result.content[0].text
                if "Unstaged changes:" in content and len(content.strip().split('\n')) > 1:
                    print(f"  {content}")
                else:
                    print("  변경사항이 없습니다.")
            except Exception as e:
                print(f"  ❌ 오류: {e}")
            print()
            
            # 6. 스테이징된 변경사항 확인
            print("📝 스테이징된 변경사항: \n\tsession.call_tool('git_diff_staged', {'repo_path': '../..', 'context_lines': 3})")
            try:
                result = await session.call_tool("git_diff_staged", {
                    "repo_path": "../..",
                    "context_lines": 3
                })
                content = result.content[0].text
                if "Staged changes:" in content and len(content.strip().split('\n')) > 1:
                    print(f"  {content}")
                else:
                    print("  스테이징된 변경사항이 없습니다.")
            except Exception as e:
                print(f"  ❌ 오류: {e}")
            print()
            
            # 7. 원격 브랜치 목록 확인
            print("🌐 원격 브랜치 목록: \n\tsession.call_tool('git_branch', {'repo_path': '../..', 'branch_type': 'remote'})")
            try:
                result = await session.call_tool("git_branch", {
                    "repo_path": "../..",
                    "branch_type": "remote"
                })
                print(f"  {result.content[0].text}")
            except Exception as e:
                print(f"  ❌ 오류: {e}")
            print()
            
            # 8. 최신 커밋 상세 정보
            print("🔎 최신 커밋 상세 정보: \n\tsession.call_tool('git_show', {'repo_path': '../..', 'revision': 'HEAD'})")
            try:
                result = await session.call_tool("git_show", {
                    "repo_path": "../..",
                    "revision": "HEAD"
                })
                content = result.content[0].text
                # 너무 길 수 있으므로 앞부분만 표시
                lines = content.split('\n')
                if len(lines) > 20:
                    print('\n'.join(lines[:20]))
                    print("  ... (생략)")
                else:
                    print(f"  {content}")
            except Exception as e:
                print(f"  ❌ 오류: {e}")
            print()
            
            print("✅ 모든 테스트 완료!")

if __name__ == "__main__":
    asyncio.run(test_git_server()) 
    
# -- test
# cd ./ch99-reference-servers/git-server
# uv run python test_git_client.py 
