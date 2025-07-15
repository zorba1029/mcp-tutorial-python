#!/usr/bin/env python3
"""
Elicitation 서버 테스트 클라이언트
elicitation-server.py를 테스트하기 위한 클라이언트
"""
import asyncio
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
import json

# 서버 파라미터 설정
server_params = StdioServerParameters(
    command="uv",
    args=["run", "python", "elicitation-server.py"],
    env=None,
    name="Elicitation Demo"
)

class ElicitationLogCollector:
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

async def elicitation_handler(context, params):
    """Elicitation 요청 처리"""
    print(f"\n🤖 Elicitation 요청:")
    print(f"메시지: {params.message}")
    print(f"스키마: {params.schema.__name__ if hasattr(params.schema, '__name__') else params.schema}")
    
    # 사용자 입력 받기
    if "다른 날짜" in params.message:
        # 예약 대체 날짜 확인
        print(f"질문: {params.message}")
        
        check_alt = input("다른 날짜를 확인하시겠습니까? (y/n): ").lower().strip()
        
        if check_alt in ['y', 'yes', '예', '네']:
            alt_date = input("원하는 대체 날짜를 입력하세요 (YYYY-MM-DD): ").strip()
            response_data = {
                "checkAlternative": True,
                "alternativeDate": alt_date
            }
            print(f"📝 사용자 응답: {response_data}")
            return types.ElicitResult(action="accept", content=response_data)
        else:
            response_data = {
                "checkAlternative": False,
                "alternativeDate": "2024-12-26"  # 기본값
            }
            print(f"📝 사용자 응답: {response_data}")
            return types.ElicitResult(action="accept", content=response_data)
    
    elif "배송 옵션" in params.message:
        # 배송 옵션 선택
        print(f"질문: {params.message}")
        
        delivery_type = input("배송 방법을 선택하세요 (standard/express/overnight): ").strip()
        gift_wrap = input("선물 포장을 원하시나요? (y/n): ").lower().strip() in ['y', 'yes', '예', '네']
        special_instructions = input("특별 요청사항 (없으면 엔터): ").strip()
        
        response_data = {
            "deliveryType": delivery_type if delivery_type else "standard",
            "giftWrap": gift_wrap,
            "specialInstructions": special_instructions if special_instructions else None
        }
        print(f"📝 사용자 응답: {response_data}")
        return types.ElicitResult(action="accept", content=response_data)
    
    elif "결제 방법" in params.message:
        # 결제 방법 선택
        print(f"질문: {params.message}")
        
        method = input("결제 수단을 선택하세요 (card/bank/paypal): ").strip()
        save_for_future = input("다음에도 사용하기 위해 저장하시겠습니까? (y/n): ").lower().strip() in ['y', 'yes', '예', '네']
        
        response_data = {
            "method": method if method else "card",
            "saveForFuture": save_for_future
        }
        print(f"📝 사용자 응답: {response_data}")
        return types.ElicitResult(action="accept", content=response_data)
    
    elif "알림" in params.message:
        # 알림 설정
        print(f"질문: {params.message}")
        
        if "설정하시겠습니까" in params.message:
            enable = input("알림을 받으시겠습니까? (y/n): ").lower().strip() in ['y', 'yes', '예', '네']
            if enable:
                email = input("이메일로 받으시겠습니까? (y/n): ").lower().strip() in ['y', 'yes', '예', '네']
                sms = input("SMS로 받으시겠습니까? (y/n): ").lower().strip() in ['y', 'yes', '예', '네']
                response_data = {
                    "enable": True,
                    "email": email,
                    "sms": sms
                }
            else:
                response_data = {
                    "enable": False,
                    "email": False,
                    "sms": False
                }
        else:
            frequency = input("알림 빈도를 선택하세요 (immediate/daily/weekly): ").strip()
            quiet_hours = input("방해 금지 시간을 설정하시겠습니까? (y/n): ").lower().strip() in ['y', 'yes', '예', '네']
            response_data = {
                "frequency": frequency if frequency else "daily",
                "quiet_hours": quiet_hours
            }
        print(f"📝 사용자 응답: {response_data}")
        return types.ElicitResult(action="accept", content=response_data)
    
    else:
        print("📝 기본 응답: 취소")
        return types.ElicitResult(action="cancel")

async def test_elicitation_server():
    """Elicitation 서버 테스트"""
    log_collector = ElicitationLogCollector()
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write, 
                                 logging_callback=log_collector, elicitation_callback=elicitation_handler) as session:
            # 서버 초기화
            await session.initialize()
            print("✅ 서버에 연결되었습니다.\n")
            
            print("🚀 Elicitation 서버 테스트 시작\n")
            
            # 1. 서버 정보 확인
            print("=" * 60)
            print("1️⃣ 서버 정보 확인")
            print("=" * 60)
            
            # 도구 목록 확인
            tools = await session.list_tools()
            print(f"사용 가능한 도구: {len(tools.tools)}개")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")
            print()
            
            # 리소스 목록 확인
            resources = await session.list_resources()
            print(f"사용 가능한 리소스: {len(resources.resources)}개")
            for resource in resources.resources:
                print(f"  - {resource.uri}: {resource.name}")
            print()
            
            # 2. 리소스 읽기 테스트
            print("\n" + "=" * 60)
            print("2️⃣ 리소스 읽기 테스트")
            print("=" * 60)
            
            try:
                info_resource = await session.read_resource("info://elicitation")
                print("Elicitation 정보:")
                print(info_resource.contents[0].text)
                print()
            except Exception as e:
                print(f"리소스 읽기 실패: {e}")
                print()
            
            # 3. 예약 도구 테스트 (정상 케이스)
            print("\n" + "=" * 60)
            print("3️⃣ 예약 도구 테스트 - 정상 케이스")
            print("=" * 60)
            
            try:
                booking_result = await session.call_tool(
                    "book_table",
                    arguments={
                        "date": "2024-12-24",
                        "time": "19:00",
                        "party_size": 4
                    }
                )
                print("예약 결과:")
                for content in booking_result.content:
                    if content.type == "text":
                        print(content.text)
                print()
            except Exception as e:
                print(f"예약 도구 테스트 실패: {e}")
                print()
            
            # 4. 예약 도구 테스트 (Elicitation 트리거)
            print("\n" + "=" * 60)
            print("4️⃣ 예약 도구 테스트 - Elicitation 트리거")
            print("=" * 60)
            
            try:
                # 이 테스트는 실제 MCP 클라이언트에서만 완전히 작동
                # 여기서는 elicitation이 트리거되는지만 확인
                booking_result = await session.call_tool(
                    "book_table",
                    arguments={
                        "date": "2024-12-25",  # 예약 불가 날짜
                        "time": "19:00",
                        "party_size": 2
                    }
                )
                print("예약 결과 (Elicitation 트리거):")
                for content in booking_result.content:
                    if content.type == "text":
                        print(content.text)
                print()
            except Exception as e:
                print(f"Elicitation 예약 테스트 실패: {e}")
                print()
            
            # 5. 주문 처리 테스트
            print("\n" + "=" * 60)
            print("5️⃣ 주문 처리 테스트")
            print("=" * 60)
            
            try:
                order_result = await session.call_tool(
                    "process_order",
                    arguments={
                        "items": ["상품1", "상품2", "상품3"],
                        "total_amount": 99.99
                    }
                )
                print("주문 처리 결과:")
                for content in order_result.content:
                    if content.type == "text":
                        print(content.text)
                print()
            except Exception as e:
                print(f"주문 처리 테스트 실패: {e}")
                print()
            
            # 6. 알림 설정 테스트
            print("\n" + "=" * 60)
            print("6️⃣ 알림 설정 테스트")
            print("=" * 60)
            
            try:
                notification_result = await session.call_tool(
                    "configure_notification",
                    arguments={
                        "notification_type": "주문 상태"
                    }
                )
                print("알림 설정 결과:")
                for content in notification_result.content:
                    if content.type == "text":
                        print(content.text)
                print()
            except Exception as e:
                print(f"알림 설정 테스트 실패: {e}")
                print()
            
            # 최종 통계
            print("\n" + "=" * 60)
            print("📊 로그 통계")
            print("=" * 60)
            print(f"총 로그 메시지: {len(log_collector.logs)}개")
            
            # 레벨별 통계
            level_counts = {}
            for log in log_collector.logs:
                level = log['level']
                level_counts[level] = level_counts.get(level, 0) + 1
            
            print("\n로그 레벨별 통계:")
            for level, count in sorted(level_counts.items()):
                print(f"  {level}: {count}개")
            
            print("\n✅ 모든 테스트 완료!")
            print("\n📝 참고사항:")
            print("- Elicitation 기능은 완전한 MCP 클라이언트(예: Claude Desktop)에서만 정상 작동합니다")
            print("- 이 테스트 클라이언트에서는 elicitation이 트리거되지만 사용자 응답은 처리되지 않습니다")
            print("- 실제 대화형 테스트를 위해서는 Claude Desktop 등의 클라이언트를 사용하세요")

async def interactive_test():
    """대화형 테스트 모드"""
    log_collector = ElicitationLogCollector()
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write, 
                                 logging_callback=log_collector, elicitation_callback=elicitation_handler) as session:
            await session.initialize()
            print("✅ 서버에 연결되었습니다.\n")
            
            print("🎮 대화형 테스트 모드")
            print("사용 가능한 명령:")
            print("1. book - 테이블 예약")
            print("2. order - 주문 처리") 
            print("3. notify - 알림 설정")
            print("4. info - 서버 정보")
            print("5. quit - 종료")
            print()
            
            while True:
                command = input("명령을 입력하세요: ").strip().lower()
                
                if command == "quit":
                    break
                
                elif command == "book":
                    date = input("날짜 (YYYY-MM-DD): ")
                    time = input("시간 (HH:MM): ")
                    party_size = int(input("인원수: "))
                    
                    try:
                        result = await session.call_tool(
                            "book_table",
                            arguments={
                                "date": date,
                                "time": time,
                                "party_size": party_size
                            }
                        )
                        for content in result.content:
                            if content.type == "text":
                                print(content.text)
                    except Exception as e:
                        print(f"오류: {e}")
                
                elif command == "order":
                    items_str = input("상품 목록 (쉼표로 구분): ")
                    items = [item.strip() for item in items_str.split(",")]
                    amount = float(input("총 금액: "))
                    
                    try:
                        result = await session.call_tool(
                            "process_order",
                            arguments={
                                "items": items,
                                "total_amount": amount
                            }
                        )
                        for content in result.content:
                            if content.type == "text":
                                print(content.text)
                    except Exception as e:
                        print(f"오류: {e}")
                
                elif command == "notify":
                    notification_type = input("알림 유형: ")
                    
                    try:
                        result = await session.call_tool(
                            "configure_notification",
                            arguments={
                                "notification_type": notification_type
                            }
                        )
                        for content in result.content:
                            if content.type == "text":
                                print(content.text)
                    except Exception as e:
                        print(f"오류: {e}")
                
                elif command == "info":
                    try:
                        tools = await session.list_tools()
                        resources = await session.list_resources()
                        
                        print(f"도구: {len(tools.tools)}개")
                        for tool in tools.tools:
                            print(f"  - {tool.name}")
                        
                        print(f"리소스: {len(resources.resources)}개")
                        for resource in resources.resources:
                            print(f"  - {resource.uri}")
                    except Exception as e:
                        print(f"오류: {e}")
                
                else:
                    print("알 수 없는 명령입니다.")
                
                print()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        print("🎮 대화형 모드로 실행합니다...")
        print("=" * 60)
        asyncio.run(interactive_test())
        print("\n✨ 테스트 완료!")
    else:
        print("🚀 자동 테스트 모드로 실행합니다...")
        print("=" * 60)
        asyncio.run(test_elicitation_server())
        print("\n✨ 테스트 완료!")