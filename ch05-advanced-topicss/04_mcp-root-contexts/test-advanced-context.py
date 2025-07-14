#!/usr/bin/env python3
"""
Context 고급 기능 테스트 클라이언트
"""
import asyncio
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
import json
from typing import Optional

# 서버 파라미터 설정
server_params = StdioServerParameters(
    command="uv",
    args=["run", "python", "context-advanced-server.py"],
    env=None,
    name="Advanced Context Demo"
)

class AdvancedLogCollector:
    """고급 로그 수집기"""
    def __init__(self):
        self.logs = []
        self.progress_updates = []
        
    async def __call__(self, params: types.LoggingMessageNotificationParams) -> None:
        log_entry = {
            "level": params.level,
            "message": params.data,
            "timestamp": getattr(params, 'timestamp', None)
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

class NotificationHandler:
    """알림 처리기"""
    def __init__(self):
        self.notifications = []
        
    async def __call__(self, message) -> None:
        if isinstance(message, types.ServerNotification):
            self.notifications.append(message)
            
            # 진행 상황 알림 특별 처리
            if hasattr(message, 'method') and 'progress' in str(message.method):
                print(f"📊 진행 상황: {message}")
            else:
                print(f"🔔 알림: {type(message).__name__}")

async def test_task_session(session: ClientSession):
    """작업 세션 테스트"""
    print("\n" + "="*60)
    print("🧪 작업 세션 생성 및 실행 테스트")
    print("="*60)
    
    # 1. 작업 세션 생성
    print("\n1️⃣ 작업 세션 생성")
    result = await session.call_tool(
        "create_task_session",
        arguments={
            "task_name": "데이터 분석 작업",
            "description": "대용량 로그 파일 분석"
        }
    )
    
    if result.content:
        try:
            # 디버깅을 위한 raw content 출력
            print(f"Raw content: {result.content}")
            if result.content and len(result.content) > 0:
                content = result.content[0]
                print(f"Content type: {type(content)}")
                print(f"Content text: {getattr(content, 'text', 'No text attribute')}")
                
                if hasattr(content, 'text'):
                    data = json.loads(content.text)
                    session_id = data.get('session_id')
                    print(f"✅ 세션 생성됨: {session_id}")
                    print(f"   설정: {data.get('config')}")
                else:
                    print("❌ Content has no text attribute")
                    return
        except json.JSONDecodeError as e:
            print(f"❌ JSON 파싱 오류: {e}")
            print(f"   Raw text: {content.text if hasattr(content, 'text') else 'N/A'}")
            return
        except Exception as e:
            print(f"❌ 예상치 못한 오류: {e}")
            return
        
        # 2. 작업 실행
        print("\n2️⃣ 작업 실행")
        exec_result = await session.call_tool(
            "execute_task",
            arguments={"session_id": session_id}
        )
        
        if exec_result.content:
            exec_data = json.loads(exec_result.content[0].text)
            print(f"✅ 작업 완료: {exec_data.get('status')}")
            print(f"   실행 시간: {exec_data.get('execution_time')}")
        
        # 3. 세션 정보 조회 (리소스)
        print("\n3️⃣ 세션 정보 조회")
        resource_uri = f"task://session/{session_id}"
        resource = await session.read_resource(resource_uri)
        if resource.contents:
            print(f"📄 세션 정보:\n{resource.contents[0].text}")

async def test_batch_processing(session: ClientSession):
    """배치 처리 테스트"""
    print("\n" + "="*60)
    print("🧪 배치 데이터 처리 테스트")
    print("="*60)
    
    # 테스트 데이터
    test_items = [
        "log_2024_01_01.txt",
        "log_2024_01_02.txt",
        "log_2024_01_03.txt",
        "log_2024_01_04.txt",
        "log_2024_01_05.txt"
    ]
    
    result = await session.call_tool(
        "process_data_batch",
        arguments={"data_items": test_items}
    )
    
    if result.content:
        data = json.loads(result.content[0].text)
        print(f"\n📊 처리 결과:")
        print(f"   성공: {data.get('processed')}개")
        print(f"   실패: {data.get('failed')}개")
        print(f"   형식: {data.get('format')}")

async def test_monitoring(session: ClientSession):
    """시스템 모니터링 테스트"""
    print("\n" + "="*60)
    print("🧪 시스템 모니터링 테스트")
    print("="*60)
    
    print("\n5초간 시스템 모니터링을 시작합니다...")
    
    result = await session.call_tool(
        "monitor_system",
        arguments={"duration_seconds": 5}
    )
    
    if result.content:
        data = json.loads(result.content[0].text)
        summary = data.get('summary', {})
        
        print(f"\n📈 모니터링 요약:")
        print(f"   평균 CPU: {summary.get('avg_cpu')}%")
        print(f"   평균 메모리: {summary.get('avg_memory')}%")
        print(f"   최대 CPU: {summary.get('max_cpu')}%")
        print(f"   최대 메모리: {summary.get('max_memory')}%")

async def test_resources(session: ClientSession):
    """리소스 테스트"""
    print("\n" + "="*60)
    print("🧪 리소스 접근 테스트")
    print("="*60)
    
    # 활성 작업 목록 조회
    print("\n📋 활성 작업 목록 조회")
    resource = await session.read_resource("tasks://active")
    if resource.contents:
        data = json.loads(resource.contents[0].text)
        print(f"활성 작업 수: {data.get('active_tasks')}개")

async def run():
    """메인 실행 함수"""
    log_collector = AdvancedLogCollector()
    notification_handler = NotificationHandler()
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(
            read,
            write,
            logging_callback=log_collector,
            message_handler=notification_handler
        ) as session:
            
            # 세션 초기화
            await session.initialize()
            print("✅ 서버에 연결되었습니다.")
            
            # 사용 가능한 도구 확인
            tools = await session.list_tools()
            print(f"\n📋 사용 가능한 도구: {len(tools.tools)}개")
            for tool in tools.tools:
                print(f"  - {tool.name}")
            
            # 테스트 실행
            try:
                # 1. 작업 세션 테스트
                await test_task_session(session)
                
                # 2. 배치 처리 테스트
                await test_batch_processing(session)
                
                # 3. 모니터링 테스트
                await test_monitoring(session)
                
                # 4. 리소스 테스트
                await test_resources(session)
                
            except Exception as e:
                print(f"\n❌ 테스트 중 오류 발생: {e}")
            
            # 최종 통계
            print("\n" + "="*60)
            print("📊 최종 통계")
            print("="*60)
            print(f"총 로그 메시지: {len(log_collector.logs)}개")
            print(f"총 알림: {len(notification_handler.notifications)}개")
            
            # 로그 레벨별 통계
            level_counts = {}
            for log in log_collector.logs:
                level = log['level']
                level_counts[level] = level_counts.get(level, 0) + 1
            
            print("\n로그 레벨별 통계:")
            for level, count in sorted(level_counts.items()):
                print(f"  {level}: {count}개")

if __name__ == "__main__":
    print("🚀 Context 고급 기능 테스트 시작")
    print("="*60)
    asyncio.run(run())
    print("\n✨ 테스트 완료!") 