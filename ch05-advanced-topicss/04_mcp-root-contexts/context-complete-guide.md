# MCP Context 완벽 가이드

## 개요

Context는 MCP(Model Context Protocol)에서 도구(tool)와 리소스(resource)가 클라이언트와 상호작용할 수 있게 해주는 핵심 객체입니다. [GitHub의 context.py](https://github.com/modelcontextprotocol/python-sdk/blob/main/src/mcp/shared/context.py)에서 구현을 확인할 수 있습니다.

## Context의 주요 기능

### 1. 로깅 (Logging)
다양한 레벨의 로그 메시지를 클라이언트에 전송할 수 있습니다.

```python
# 로그 레벨
await ctx.debug("디버그 정보")      # 개발 시 상세 정보
await ctx.info("일반 정보")         # 일반적인 정보성 메시지
await ctx.warning("경고 메시지")     # 주의가 필요한 상황
await ctx.error("오류 발생")        # 오류 상황
await ctx.critical("심각한 오류")   # 시스템 중단 수준의 오류
```

### 2. 진행 상황 보고 (Progress Reporting)
긴 작업의 진행 상황을 실시간으로 보고합니다.

```python
await ctx.report_progress(
    progress=0.5,      # 현재 진행률
    total=1.0,         # 전체 작업량
    message="50% 완료"  # 상태 메시지
)
```

### 3. 사용자 입력 요청 (Elicitation)
작업 중 사용자에게 추가 정보나 선택을 요청할 수 있습니다.

```python
from pydantic import BaseModel, Field

class UserInput(BaseModel):
    choice: str = Field(description="사용자 선택")
    confirm: bool = Field(description="확인 여부")

result = await ctx.elicit(
    message="옵션을 선택해주세요",
    schema=UserInput
)

if result.action == "accept" and result.data:
    # 사용자가 입력을 제공한 경우
    user_choice = result.data.choice
```

### 4. 세션 접근 (Session Access)
현재 세션에 대한 접근과 알림을 제공합니다.

```python
# 리소스 목록이 변경되었음을 알림
await ctx.session.send_resource_list_changed()

# 도구 목록이 변경되었음을 알림
await ctx.session.send_tool_list_changed()
```

## 실제 사용 예제

### 기본 예제: 날씨 서버
```python
from mcp.server.fastmcp import FastMCP, Context

mcp = FastMCP("Weather Server")

@mcp.tool()
async def get_weather(location: str, ctx: Context) -> dict:
    """Context를 활용한 날씨 정보 조회"""
    
    # 시작 로그
    await ctx.info(f"날씨 정보 조회 시작: {location}")
    
    # 진행 상황 보고
    await ctx.report_progress(0.3, 1.0, "API 연결 중...")
    
    # API 호출 시뮬레이션
    await asyncio.sleep(1)
    
    await ctx.report_progress(0.7, 1.0, "데이터 처리 중...")
    
    weather_data = {
        "location": location,
        "temperature": 22,
        "description": "맑음"
    }
    
    # 완료 로그
    await ctx.info(f"날씨 정보 조회 완료: {location}")
    
    return weather_data
```

### 고급 예제: 작업 세션 관리
```python
@mcp.tool()
async def create_task_session(
    task_name: str,
    description: str,
    ctx: Context
) -> Dict[str, Any]:
    """복잡한 작업 세션 생성"""
    
    # 디버그 정보
    await ctx.debug(f"세션 생성 요청: {task_name}")
    
    # 사용자 설정 요청
    config_result = await ctx.elicit(
        message="작업 설정을 구성해주세요",
        schema=TaskConfiguration
    )
    
    if config_result.action != "accept":
        await ctx.warning("사용자가 설정을 취소했습니다")
        return {"status": "cancelled"}
    
    # 세션 생성
    session_id = create_session(task_name, config_result.data)
    
    # 리소스 목록 업데이트 알림
    await ctx.session.send_resource_list_changed()
    
    await ctx.info(f"세션 생성 완료: {session_id}")
    
    return {"session_id": session_id, "status": "created"}
```

### 배치 처리 예제
```python
@mcp.tool()
async def process_batch(
    items: List[str],
    ctx: Context
) -> Dict[str, Any]:
    """배치 처리 with 상세 진행 상황"""
    
    total_items = len(items)
    processed = []
    errors = []
    
    await ctx.info(f"{total_items}개 항목 처리 시작")
    
    for idx, item in enumerate(items):
        try:
            # 진행률 계산 및 보고
            progress = (idx + 1) / total_items
            await ctx.report_progress(
                progress=progress,
                total=1.0,
                message=f"처리 중: {item} ({idx + 1}/{total_items})"
            )
            
            # 항목 처리
            result = await process_item(item)
            processed.append(result)
            
            # 개별 항목 완료 로그
            await ctx.debug(f"완료: {item}")
            
        except Exception as e:
            await ctx.error(f"처리 실패: {item} - {str(e)}")
            errors.append({"item": item, "error": str(e)})
    
    # 최종 결과 보고
    if errors:
        await ctx.warning(f"{len(errors)}개 항목 처리 실패")
    
    await ctx.info(f"배치 처리 완료: 성공 {len(processed)}개, 실패 {len(errors)}개")
    
    return {
        "processed": processed,
        "errors": errors,
        "summary": {
            "total": total_items,
            "success": len(processed),
            "failed": len(errors)
        }
    }
```

## Context 사용 시 주의사항

### 1. 비동기 함수 필수
Context를 사용하는 모든 함수는 `async def`로 선언되어야 합니다.

```python
# ❌ 잘못된 예
@mcp.tool()
def sync_tool(ctx: Context):  # 동기 함수는 Context 사용 불가
    ctx.info("This won't work")  # await 없이는 호출 불가

# ✅ 올바른 예
@mcp.tool()
async def async_tool(ctx: Context):
    await ctx.info("This works!")
```

### 2. 에러 처리
Context 메서드 호출 시 에러가 발생할 수 있으므로 적절한 에러 처리가 필요합니다.

```python
try:
    result = await ctx.elicit(
        message="입력해주세요",
        schema=MySchema
    )
except Exception as e:
    await ctx.error(f"사용자 입력 요청 실패: {str(e)}")
    return {"status": "error", "message": str(e)}
```

### 3. 클라이언트 호환성
모든 클라이언트가 모든 Context 기능을 지원하는 것은 아닙니다. 

```python
# Elicitation 지원 여부 확인
if hasattr(ctx, 'elicit'):
    result = await ctx.elicit(...)
else:
    # 대체 로직
    await ctx.info("사용자 입력이 필요하지만 지원되지 않습니다")
```

## 클라이언트 구현

### 로깅 콜백
```python
class LoggingCollector:
    def __init__(self):
        self.logs = []
    
    async def __call__(self, params: types.LoggingMessageNotificationParams):
        self.logs.append({
            "level": params.level,
            "message": params.data,
            "timestamp": getattr(params, 'timestamp', None)
        })
        print(f"[{params.level.upper()}] {params.data}")
```

### 메시지 핸들러
```python
async def message_handler(message):
    if isinstance(message, types.ServerNotification):
        if hasattr(message, 'method'):
            if 'progress' in message.method:
                # 진행 상황 업데이트 처리
                print(f"Progress: {message}")
            elif 'resource' in message.method:
                # 리소스 변경 알림 처리
                print(f"Resource changed: {message}")
```

### 클라이언트 세션 설정
```python
async with ClientSession(
    read,
    write,
    logging_callback=LoggingCollector(),
    message_handler=message_handler
) as session:
    # 도구 호출
    result = await session.call_tool(
        "my_tool",
        arguments={"param": "value"}
    )
```

## 실행 방법

### 서버 실행
```bash
# Context를 사용하는 서버 실행
uv run python context-advanced-server.py

# MCP Inspector로 테스트
uv run mcp dev context-advanced-server.py
```

### 클라이언트 실행
```bash
# 테스트 클라이언트 실행
uv run python test-advanced-context.py
```

## 베스트 프랙티스

1. **적절한 로그 레벨 사용**
   - `debug`: 개발 시 상세 정보
   - `info`: 일반적인 진행 상황
   - `warning`: 주의가 필요한 상황
   - `error`: 복구 가능한 오류
   - `critical`: 시스템 중단 수준

2. **진행 상황 보고 빈도**
   - 너무 자주 보고하면 성능 저하
   - 너무 드물면 사용자 경험 저하
   - 일반적으로 1초에 1-2회가 적당

3. **Elicitation 사용**
   - 꼭 필요한 경우에만 사용
   - 명확한 스키마와 설명 제공
   - 사용자가 취소할 경우 대비

4. **세션 알림**
   - 리소스나 도구 목록이 변경될 때만 알림
   - 과도한 알림은 피하기

## 정리

Context는 MCP 서버를 더욱 강력하고 사용자 친화적으로 만드는 핵심 기능입니다. 로깅, 진행 상황 보고, 사용자 상호작용 등을 통해 풍부한 사용자 경험을 제공할 수 있습니다.

주요 장점:
- 실시간 피드백 제공
- 디버깅 용이성
- 사용자와의 상호작용
- 세션 상태 관리

Context를 적절히 활용하면 단순한 도구를 넘어 완전한 애플리케이션 수준의 기능을 제공할 수 있습니다. 