#!/usr/bin/env python3
import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_weather_server():
    """MCP weather server를 테스트하는 클라이언트"""
    
    # 서버 파라미터 설정
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "01_weather-server.py"],
        env=None
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 서버 초기화
            await session.initialize()
            
            # 사용 가능한 도구 목록 가져오기
            tools = await session.list_tools()
            print("사용 가능한 도구들:")
            for tool in tools.tools:
                print(f"- {tool.name}: {tool.description}")
            print()
            
            # get_weather 도구 테스트
            print("=== get_weather 테스트 ===")
            result = await session.call_tool("get_weather", {"location": "서울"})
            print(f"서울 날씨: {json.dumps(result.content[0].text, indent=2, ensure_ascii=False)}")
            print()
            
            # forecast 도구 테스트
            print("=== forecast 테스트 ===")
            result = await session.call_tool("forecast", {"location": "부산", "days": 3})
            print(f"부산 3일 예보: {json.dumps(result.content[0].text, indent=2, ensure_ascii=False)}")
            print()
            
            # 다른 지역 테스트
            print("=== 다양한 지역 테스트 ===")
            locations = ["도쿄", "뉴욕", "런던"]
            for location in locations:
                result = await session.call_tool("get_weather", {"location": location})
                weather_data = json.loads(result.content[0].text)
                print(f"{location}: {weather_data['temperature']}°C, {weather_data['description']}")


if __name__ == "__main__":
    print("MCP Weather Server 클라이언트 테스트 시작...")
    asyncio.run(test_weather_server())
    print("테스트 완료!") 