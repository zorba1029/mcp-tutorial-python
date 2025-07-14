#!/usr/bin/env python3
"""
Elicitation 기능을 보여주는 MCP 서버 예제
GitHub 공식 예제 참고: https://github.com/modelcontextprotocol/python-sdk/blob/main/examples/snippets/servers/elicitation.py
"""
from pydantic import BaseModel, Field
from mcp.server.fastmcp import Context, FastMCP
from datetime import datetime
from typing import Optional

# Note: elicitation requires MCP client support
# This example shows the proper implementation structure

mcp = FastMCP(name="Elicitation Demo")

# 다양한 Elicitation 스키마들

class BookingPreferences(BaseModel):
    """레스토랑 예약 설정"""
    checkAlternative: bool = Field(description="다른 날짜를 확인하시겠습니까?")
    alternativeDate: str = Field(
        default="2024-12-26",
        description="대체 날짜 (YYYY-MM-DD)",
    )

class DeliveryOptions(BaseModel):
    """배송 옵션 선택"""
    deliveryType: str = Field(
        default="standard",
        description="배송 방법 (standard/express/overnight)"
    )
    giftWrap: bool = Field(
        default=False,
        description="선물 포장 여부"
    )
    specialInstructions: Optional[str] = Field(
        default=None,
        description="특별 요청사항"
    )

class PaymentMethod(BaseModel):
    """결제 방법 선택"""
    method: str = Field(
        description="결제 수단 (card/bank/paypal)"
    )
    saveForFuture: bool = Field(
        default=False,
        description="다음에도 사용하기 위해 저장"
    )

@mcp.tool()
async def book_table(
    date: str,
    time: str,
    party_size: int,
    ctx: Context,
) -> str:
    """레스토랑 테이블 예약 with Elicitation"""
    
    await ctx.info(f"예약 요청: {date} {time}, {party_size}명")
    
    # 특정 날짜는 예약 불가
    if date == "2024-12-25":
        await ctx.warning(f"{date}는 예약이 가득 찼습니다")
        
        # 사용자에게 대체 날짜 확인
        result = await ctx.elicit(
            message=f"{party_size}명 예약이 {date}에는 불가능합니다. 다른 날짜를 확인하시겠습니까?",
            schema=BookingPreferences,
        )

        if result.action == "accept" and result.data:
            if result.data.checkAlternative:
                await ctx.info(f"대체 날짜로 예약 진행: {result.data.alternativeDate}")
                return f"✅ 예약 완료: {result.data.alternativeDate} {time}, {party_size}명"
            else:
                await ctx.info("고객이 대체 날짜를 원하지 않음")
                return "❌ 예약이 취소되었습니다"
        
        await ctx.info("고객이 응답하지 않음")
        return "❌ 예약이 취소되었습니다 (응답 없음)"

    # 예약 가능한 경우
    await ctx.info(f"예약 완료: {date} {time}")
    return f"✅ 예약 완료: {date} {time}, {party_size}명"

@mcp.tool()
async def process_order(
    items: list[str],
    total_amount: float,
    ctx: Context,
) -> str:
    """주문 처리 with 배송 옵션 선택"""
    
    await ctx.info(f"주문 처리 시작: {len(items)}개 상품, 총 ${total_amount}")
    
    # 배송 옵션 선택 요청
    delivery_result = await ctx.elicit(
        message="배송 옵션을 선택해주세요",
        schema=DeliveryOptions
    )
    
    if delivery_result.action != "accept" or not delivery_result.data:
        await ctx.warning("배송 옵션이 선택되지 않음")
        return "❌ 주문이 취소되었습니다"
    
    delivery = delivery_result.data
    
    # 배송비 계산
    shipping_cost = {
        "standard": 5.0,
        "express": 15.0,
        "overnight": 30.0
    }.get(delivery.deliveryType, 5.0)
    
    if delivery.giftWrap:
        shipping_cost += 3.0
    
    final_total = total_amount + shipping_cost
    
    # 결제 방법 선택
    payment_result = await ctx.elicit(
        message=f"총 ${final_total:.2f} (배송비 포함) - 결제 방법을 선택해주세요",
        schema=PaymentMethod
    )
    
    if payment_result.action != "accept" or not payment_result.data:
        await ctx.warning("결제 방법이 선택되지 않음")
        return "❌ 주문이 취소되었습니다"
    
    payment = payment_result.data
    
    # 주문 완료
    order_id = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    result = f"""
✅ 주문 완료!
주문 번호: {order_id}
상품: {len(items)}개
배송: {delivery.deliveryType}
선물 포장: {'예' if delivery.giftWrap else '아니오'}
결제: {payment.method}
총액: ${final_total:.2f}
"""
    
    if delivery.specialInstructions:
        result += f"특별 요청: {delivery.specialInstructions}\n"
    
    await ctx.info(f"주문 완료: {order_id}")
    
    return result

@mcp.tool()
async def configure_notification(
    notification_type: str,
    ctx: Context,
) -> str:
    """알림 설정 with 다단계 Elicitation"""
    
    await ctx.info(f"알림 설정 시작: {notification_type}")
    
    # 첫 번째 질문: 알림 받을지 여부
    class NotificationEnable(BaseModel):
        enable: bool = Field(description="알림을 받으시겠습니까?")
        email: bool = Field(default=True, description="이메일로 받기")
        sms: bool = Field(default=False, description="SMS로 받기")
    
    enable_result = await ctx.elicit(
        message=f"{notification_type} 알림을 설정하시겠습니까?",
        schema=NotificationEnable
    )
    
    if enable_result.action != "accept" or not enable_result.data:
        return "❌ 알림 설정이 취소되었습니다"
    
    if not enable_result.data.enable:
        return "✅ 알림이 비활성화되었습니다"
    
    # 두 번째 질문: 알림 빈도
    class NotificationFrequency(BaseModel):
        frequency: str = Field(
            default="daily",
            description="알림 빈도 (immediate/daily/weekly)"
        )
        quiet_hours: bool = Field(
            default=True,
            description="방해 금지 시간 설정 (22:00-08:00)"
        )
    
    freq_result = await ctx.elicit(
        message="알림 빈도를 선택해주세요",
        schema=NotificationFrequency
    )
    
    if freq_result.action != "accept" or not freq_result.data:
        return "❌ 알림 설정이 취소되었습니다"
    
    # 설정 완료
    channels = []
    if enable_result.data.email:
        channels.append("이메일")
    if enable_result.data.sms:
        channels.append("SMS")
    
    result = f"""
✅ 알림 설정 완료!
유형: {notification_type}
채널: {', '.join(channels)}
빈도: {freq_result.data.frequency}
방해 금지: {'설정됨' if freq_result.data.quiet_hours else '설정 안 함'}
"""
    
    await ctx.info("알림 설정 완료")
    return result

# 리소스
@mcp.resource("info://elicitation")
def elicitation_info() -> str:
    """Elicitation 기능 설명"""
    return """
# Elicitation 기능

Elicitation은 도구 실행 중 사용자에게 추가 정보나 선택을 요청할 수 있는 기능입니다.

## 주요 특징:
1. Pydantic 스키마를 사용한 구조화된 입력
2. 사용자가 수락/거부/취소 가능
3. 기본값 설정 가능
4. 다단계 질문 가능

## 사용 예시:
- 예약 시 대체 날짜 확인
- 주문 시 배송 옵션 선택
- 결제 방법 선택
- 알림 설정 구성

## 주의사항:
- 완전한 MCP 클라이언트(예: Claude Desktop)에서만 정상 작동
- 일반 테스트 클라이언트에서는 제한적
"""

if __name__ == "__main__":
    mcp.run() 