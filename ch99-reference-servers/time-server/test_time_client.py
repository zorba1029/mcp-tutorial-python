#!/usr/bin/env python3
"""
Time Server 테스트 클라이언트

사용법:
1. 터미널 1에서: python -m mcp_server_time
2. 터미널 2에서: python test_time_client.py
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import subprocess
import sys

async def test_time_server():
    # time server 프로세스 시작
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "python", "-m", "mcp_server_time"],
        cwd="."
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 서버 초기화
            await session.initialize()
            
            print("🕐 Time Server 테스트 시작")
            print("=" * 50)
            
            # 1. 도구 목록 확인
            tools_result = await session.list_tools()
            print("📋 사용 가능한 도구들:")
            for tool in tools_result.tools:
                print(f"  - {tool.name}: {tool.description}")
            print()
            
            # 2. 현재 시간 조회 (한국 시간)
            print("🇰🇷 한국 현재 시간:")
            result = await session.call_tool("get_current_time", {
                "timezone": "Asia/Seoul"
            })
            print(f"  {result.content[0].text}")
            print()
            
            # 3. 현재 시간 조회 (뉴욕 시간)
            print("🗽 뉴욕 현재 시간:")
            result = await session.call_tool("get_current_time", {
                "timezone": "America/New_York"
            })
            print(f"  {result.content[0].text}")
            print()
            
            # 4. 현재 시간 조회 (런던 시간)
            print("🇬🇧 런던 현재 시간:")
            result = await session.call_tool("get_current_time", {
                "timezone": "Europe/London"
            })
            print(f"  {result.content[0].text}")
            print()
            
            # 5. 시간 변환 테스트
            print("🔄 시간 변환 테스트 (한국 오후 3시 → 뉴욕):")
            result = await session.call_tool("convert_time", {
                "source_timezone": "Asia/Seoul",
                "time": "15:00",
                "target_timezone": "America/New_York"
            })
            print(f"  {result.content[0].text}")
            print()
            
            # 6. 시간 변환 테스트 2
            print("🔄 시간 변환 테스트 (런던 오전 9시 → 도쿄):")
            result = await session.call_tool("convert_time", {
                "source_timezone": "Europe/London", 
                "time": "09:00",
                "target_timezone": "Asia/Tokyo"
            })
            print(f"  {result.content[0].text}")
            print()
            
            print("✅ 모든 테스트 완료!")

if __name__ == "__main__":
    asyncio.run(test_time_server()) 
    
# -- test
# cd ./ch99-reference-servers/time-server
# uv run python test_time_client.py
