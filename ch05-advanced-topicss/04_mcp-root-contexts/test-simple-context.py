#!/usr/bin/env python3
"""
간단한 Context 기능 테스트 클라이언트
"""
import asyncio
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
import json

# 서버 파라미터 설정
server_params = StdioServerParameters(
    command="uv",
    args=["run", "python", "context-simple-server.py"],
    env=None,
    name="Simple Context Demo"
)

class SimpleLogCollector:
    """로그 수집기"""
    def __init__(self):
        self.logs = []
        
    async def __call__(self, params: types.LoggingMessageNotificationParams) -> None:
        log_entry = {
            "level": params.level,
            "message": params.data
        }
        self.logs.append(log_entry)
        
        # 로그 레벨에 따른 이모지
        emoji = {
            "debug": "🔍",
            "info": "ℹ️",
            "warning": "⚠️",
            "error": "❌",
            "critical": "🚨"
        }.get(params.level, "📝")
        
        print(f"{emoji} [{params.level.upper()}] {params.data}")

async def run():
    """메인 실행 함수"""
    log_collector = SimpleLogCollector()
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(
            read,
            write,
            logging_callback=log_collector
        ) as session:
            
            # 세션 초기화
            await session.initialize()
            print("✅ 서버에 연결되었습니다.\n")
            
            # 1. 간단한 작업 실행
            print("="*60)
            print("1️⃣ 간단한 작업 실행 (3초)")
            print("="*60)
            
            result = await session.call_tool(
                "simple_task",
                arguments={
                    "name": "데이터 백업",
                    "duration": 3
                }
            )
            
            if result.content:
                data = json.loads(result.content[0].text)
                print(f"\n✅ 결과: {data['message']}")
                print(f"   작업 ID: {data['task_id']}")
            
            print("\n" + "="*60)
            
            # 2. 배치 처리
            print("2️⃣ 배치 처리")
            print("="*60)
            
            test_items = ["item1.txt", "item2.txt", "item3.txt", "item4.txt", "item5.txt"]
            
            result = await session.call_tool(
                "batch_process",
                arguments={"items": test_items}
            )
            
            if result.content:
                data = json.loads(result.content[0].text)
                print(f"\n✅ 배치 처리 완료:")
                print(f"   전체: {data['total']}개")
                print(f"   성공: {data['processed']}개")
                print(f"   실패: {data['failed']}개")
            
            print("\n" + "="*60)
            
            # 3. 메트릭 모니터링
            print("3️⃣ 메트릭 모니터링 (5초)")
            print("="*60)
            
            result = await session.call_tool(
                "monitor_metrics",
                arguments={"seconds": 5}
            )
            
            if result.content:
                data = json.loads(result.content[0].text)
                summary = data['summary']
                print(f"\n✅ 모니터링 요약:")
                print(f"   평균 CPU: {summary['avg_cpu']:.1f}%")
                print(f"   평균 메모리: {summary['avg_memory']:.1f}%")
                print(f"   최대 CPU: {summary['max_cpu']}%")
                print(f"   최대 메모리: {summary['max_memory']}%")
            
            # 4. 리소스 조회
            print("\n" + "="*60)
            print("4️⃣ 작업 목록 조회")
            print("="*60)
            
            resource = await session.read_resource("tasks://list")
            if resource.contents:
                data = json.loads(resource.contents[0].text)
                print(f"\n📋 저장된 작업: {data['count']}개")
                for task in data['tasks']:
                    print(f"   - {task['name']} (ID: {task['id']})")
            
            # 최종 통계
            print("\n" + "="*60)
            print("📊 로그 통계")
            print("="*60)
            print(f"총 로그 메시지: {len(log_collector.logs)}개")
            
            # 레벨별 통계
            level_counts = {}
            for log in log_collector.logs:
                level = log['level']
                level_counts[level] = level_counts.get(level, 0) + 1
            
            print("\n로그 레벨별 통계:")
            for level, count in sorted(level_counts.items()):
                print(f"  {level}: {count}개")

if __name__ == "__main__":
    print("🚀 간단한 Context 테스트 시작")
    print("="*60)
    asyncio.run(run())
    print("\n✨ 테스트 완료!") 