# MCP Elicitation 기능 가이드

## Elicitation이란?

Elicitation은 MCP 도구가 실행 중에 사용자에게 추가 정보나 선택을 요청할 수 있는 기능입니다. 이를 통해 동적이고 대화형 도구를 만들 수 있습니다.

## 주요 특징

1. **구조화된 입력**: Pydantic 스키마를 사용하여 타입 안전한 입력
2. **사용자 선택권**: 수락(accept), 거부(decline), 취소(cancel) 가능
3. **기본값 지원**: 필드별 기본값 설정 가능
4. **다단계 질문**: 여러 번의 Elicitation을 연속으로 사용 가능

## 기본 사용법

```python
from pydantic import BaseModel, Field
from mcp.server.fastmcp import Context, FastMCP

# 1. 스키마 정의
class UserChoice(BaseModel):
    confirm: bool = Field(description="확인하시겠습니까?")
    reason: str = Field(default="", description="이유 (선택사항)")

# 2. 도구에서 사용
@mcp.tool()
async def my_tool(ctx: Context) -> str:
    result = await ctx.elicit(
        message="작업을 계속하시겠습니까?",
        schema=UserChoice
    )
    
    if result.action == "accept" and result.data:
        if result.data.confirm:
            return "작업을 계속합니다"
        else:
            return f"작업 중단: {result.data.reason}"
    
    return "사용자가 응답하지 않았습니다"
```

## 실제 예제

### 1. 레스토랑 예약 (GitHub 공식 예제)

```python
class BookingPreferences(BaseModel):
    checkAlternative: bool = Field(description="다른 날짜를 확인하시겠습니까?")
    alternativeDate: str = Field(
        default="2024-12-26",
        description="대체 날짜 (YYYY-MM-DD)"
    )

@mcp.tool()
async def book_table(date: str, time: str, party_size: int, ctx: Context) -> str:
    if date == "2024-12-25":  # 예약 불가능한 날짜
        result = await ctx.elicit(
            message=f"{party_size}명 예약이 {date}에는 불가능합니다. 다른 날짜를 확인하시겠습니까?",
            schema=BookingPreferences
        )
        
        if result.action == "accept" and result.data:
            if result.data.checkAlternative:
                return f"✅ 예약 완료: {result.data.alternativeDate}"
        
        return "❌ 예약 취소됨"
    
    return f"✅ 예약 완료: {date}"
```

### 2. 주문 처리 with 배송 옵션

```python
class DeliveryOptions(BaseModel):
    deliveryType: str = Field(
        default="standard",
        description="배송 방법 (standard/express/overnight)"
    )
    giftWrap: bool = Field(default=False, description="선물 포장")
    specialInstructions: Optional[str] = Field(default=None, description="특별 요청")

@mcp.tool()
async def process_order(items: list[str], ctx: Context) -> str:
    # 배송 옵션 선택
    delivery_result = await ctx.elicit(
        message="배송 옵션을 선택해주세요",
        schema=DeliveryOptions
    )
    
    if delivery_result.action == "accept" and delivery_result.data:
        # 선택된 옵션으로 주문 처리
        return f"주문 완료! 배송: {delivery_result.data.deliveryType}"
    
    return "주문 취소됨"
```

### 3. 다단계 Elicitation

```python
@mcp.tool()
async def configure_settings(ctx: Context) -> str:
    # 1단계: 기능 활성화 여부
    class EnableFeature(BaseModel):
        enable: bool = Field(description="기능을 활성화하시겠습니까?")
    
    enable_result = await ctx.elicit(
        message="새 기능을 활성화하시겠습니까?",
        schema=EnableFeature
    )
    
    if not (enable_result.action == "accept" and enable_result.data.enable):
        return "설정 변경 없음"
    
    # 2단계: 세부 설정
    class DetailedSettings(BaseModel):
        level: str = Field(default="medium", description="레벨 (low/medium/high)")
        notifications: bool = Field(default=True, description="알림 받기")
    
    detail_result = await ctx.elicit(
        message="세부 설정을 구성해주세요",
        schema=DetailedSettings
    )
    
    if detail_result.action == "accept" and detail_result.data:
        return f"설정 완료: 레벨={detail_result.data.level}"
    
    return "설정 취소됨"
```

## ElicitationResult 구조

```python
# result.action의 가능한 값:
# - "accept": 사용자가 입력을 제공하고 확인
# - "decline": 사용자가 거부
# - "cancel": 사용자가 취소

# result.data: 
# - action이 "accept"일 때만 존재
# - 스키마에 정의된 타입의 인스턴스

# result.validation_error:
# - 검증 오류가 있을 경우 오류 메시지
```

## 주의사항

### 1. 클라이언트 지원
- **완전 지원**: Claude Desktop, 공식 MCP 클라이언트
- **제한적**: 일반 테스트 클라이언트 (자동으로 거부됨)
- **미지원**: 단순 stdio 클라이언트

### 2. 에러 처리
```python
try:
    result = await ctx.elicit(message="질문", schema=MySchema)
except Exception as e:
    await ctx.error(f"Elicitation 실패: {e}")
    return "기본 동작으로 진행"
```

### 3. 사용자 경험
- 명확하고 간결한 메시지 작성
- 적절한 기본값 제공
- 취소/거부 시 대체 동작 준비

## 실행 방법

### 1. 완전한 데모 서버 테스트

`elicitation-server.py`는 전체적인 Elicitation 기능을 보여주는 완전한 데모입니다:

```bash
# 자동 테스트 모드
uv run python test-elicitation.py

# 대화형 테스트 모드 (수동 입력)
uv run python test-elicitation.py interactive
```

### 2. MCP Inspector에서 테스트
```bash
uv run mcp dev elicitation-server.py
```

### 3. Claude Desktop에 설치
```bash
uv run mcp install elicitation-server.py
```

## 활용 시나리오

1. **동적 설정**: 사용자 선호도에 따른 동작 변경
2. **오류 복구**: 실패 시 대안 제시
3. **확인 요청**: 중요한 작업 전 사용자 확인
4. **정보 수집**: 필요한 추가 정보 요청
5. **선택 분기**: 여러 옵션 중 선택

## elicitation-server.py 데모 서버

### 주요 기능

1. **테이블 예약** (`book_table`)
   - 정상 예약 처리
   - 2024-12-25 예약 불가 시 대체 날짜 확인
   - `BookingPreferences` 스키마 사용

2. **주문 처리** (`process_order`)
   - 배송 옵션 선택 (`DeliveryOptions`)
   - 결제 방법 선택 (`PaymentMethod`)
   - 단계별 사용자 입력

3. **알림 설정** (`configure_notification`)
   - 다단계 Elicitation 예제
   - 알림 활성화/비활성화
   - 알림 채널 및 빈도 설정

### 스키마 정의

```python
# 예약 설정
class BookingPreferences(BaseModel):
    checkAlternative: bool = Field(description="다른 날짜를 확인하시겠습니까?")
    alternativeDate: str = Field(default="2024-12-26", description="대체 날짜 (YYYY-MM-DD)")

# 배송 옵션
class DeliveryOptions(BaseModel):
    deliveryType: str = Field(default="standard", description="배송 방법 (standard/express/overnight)")
    giftWrap: bool = Field(default=False, description="선물 포장 여부")
    specialInstructions: Optional[str] = Field(default=None, description="특별 요청사항")

# 결제 방법
class PaymentMethod(BaseModel):
    method: str = Field(description="결제 수단 (card/bank/paypal)")
    saveForFuture: bool = Field(default=False, description="다음에도 사용하기 위해 저장")
```

## test-elicitation.py 테스트 클라이언트

### 주요 기능

1. **자동 테스트 모드** (`python test-elicitation.py`)
   - 서버 정보 확인
   - 리소스 읽기 테스트
   - 모든 도구 순차적 테스트
   - 로그 수집 및 통계

2. **대화형 테스트 모드** (`python test-elicitation.py interactive`)
   - 수동 도구 실행
   - 사용자 입력으로 테스트
   - 실시간 로그 모니터링

### 로그 수집 기능

```python
class ElicitationLogCollector:
    def __init__(self):
        self.logs = []
        
    async def __call__(self, params: types.LoggingMessageNotificationParams) -> None:
        log_entry = {
            "level": params.level,
            "message": params.data
        }
        self.logs.append(log_entry)
        
        # 로그 레벨에 따른 이모지 표시
        emoji = {
            "debug": "🔍",
            "info": "ℹ️",
            "warning": "⚠️",
            "error": "❌",
            "critical": "🚨"
        }.get(params.level, "📝")
        
        print(f"{emoji} [{params.level.upper()}] {params.data}")
```

### 테스트 실행 결과 예시

```
🚀 자동 테스트 모드로 실행합니다...
============================================================
✅ 서버에 연결되었습니다.

🚀 Elicitation 서버 테스트 시작

============================================================
1️⃣ 서버 정보 확인
============================================================
사용 가능한 도구: 3개
  - book_table: 레스토랑 테이블 예약 with Elicitation
  - process_order: 주문 처리 with 배송 옵션 선택
  - configure_notification: 알림 설정 with 다단계 Elicitation

============================================================
3️⃣ 예약 도구 테스트 - 정상 케이스
============================================================
ℹ️ [INFO] 예약 요청: 2024-12-24 19:00, 4명
ℹ️ [INFO] 예약 완료: 2024-12-24 19:00
예약 결과:
✅ 예약 완료: 2024-12-24 19:00, 4명

============================================================
4️⃣ 예약 도구 테스트 - Elicitation 트리거
============================================================
ℹ️ [INFO] 예약 요청: 2024-12-25 19:00, 2명
⚠️ [WARNING] 2024-12-25는 예약이 가득 차습니다
ℹ️ [INFO] 고객이 응답하지 않음
예약 결과 (Elicitation 트리거):
❌ 예약이 취소되었습니다 (응답 없음)

============================================================
📊 로그 통계
============================================================
총 로그 메시지: 15개

로그 레벨별 통계:
  info: 10개
  warning: 5개

✅ 모든 테스트 완료!
```

## 주요 차이점

### 이전 예제와의 차이
- **완전한 시나리오**: 실제 애플리케이션에서 사용할 수 있는 완전한 예제
- **다단계 Elicitation**: 여러 단계의 사용자 입력을 순차적으로 처리
- **조건부 로직**: 사용자 입력에 따른 다양한 처리 경로
- **실시간 로그**: 서버 로그를 실시간으로 모니터링

### 테스트 모드 비교
- **자동 모드**: 전체 기능 순차적 테스트, 로그 통계 표시
- **대화형 모드**: 사용자가 직접 입력하여 테스트 가능

## 정리

Elicitation은 MCP 도구를 더욱 대화형이고 유연하게 만드는 강력한 기능입니다. `elicitation-server.py`와 `test-elicitation.py`를 통해 실제 애플리케이션에서 사용할 수 있는 완전한 Elicitation 패턴을 학습하고 테스트할 수 있습니다. 