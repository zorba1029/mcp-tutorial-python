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

## 실제 구현 파일 개요

이 가이드는 다음 실제 구현 파일들을 기반으로 합니다:

- **`context-advanced-server.py`**: 완전한 고급 Context 서버 구현
- **`test-advanced-context.py`**: 모든 기능을 테스트하는 클라이언트
- **`context-simple-server.py`**: 기본 Context 기능만 사용하는 간단한 서버

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

## 기본 클라이언트 구성 요소

Context 기능을 제대로 활용하려면 클라이언트에서 다음 요소들을 구현해야 합니다:

### 필수 콜백 함수들
```python
# 1. 로깅 콜백 - 서버의 로그 메시지 수신
async def logging_callback(params):
    print(f"[{params.level.upper()}] {params.data}")

# 2. 메시지 핸들러 - 서버 알림 처리
async def message_handler(message):
    if isinstance(message, types.ServerNotification):
        print(f"🔔 알림: {type(message).__name__}")

# 3. Elicitation 핸들러 - 사용자 입력 요청 처리 (필수!)
async def elicitation_handler(context, params):
    # 실제 사용자 입력 처리
    return types.ElicitResult(action="accept", content=user_data)
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

## 완전한 구현 예제: context-advanced-server.py

이 섹션에서는 실제 작동하는 고급 Context 서버의 완전한 구현을 보여줍니다.

### 주요 특징
- **Elicitation**: 사용자 입력 요청 및 처리
- **Progress Reporting**: 실시간 진행 상황 보고
- **Session Management**: 작업 세션 관리
- **Resource Updates**: 동적 리소스 변경 알림
- **Multi-level Logging**: 다단계 로깅 시스템

### 핵심 구현 사항

#### 1. Pydantic 스키마 정의
```python
class TaskConfiguration(BaseModel):
    """작업 설정"""
    priority: str = Field(
        default="medium",
        description="작업 우선순위 (low/medium/high)"
    )
    notify_on_complete: bool = Field(
        default=True,
        description="완료 시 알림 여부"
    )
    max_retries: int = Field(
        default=3,
        description="최대 재시도 횟수"
    )

class DataProcessingOptions(BaseModel):
    """데이터 처리 옵션"""
    format: str = Field(
        default="json",
        description="출력 형식 (json/csv/xml)"
    )
    include_metadata: bool = Field(
        default=True,
        description="메타데이터 포함 여부"
    )
    compression: bool = Field(
        default=False,
        description="압축 여부"
    )
```

#### 2. Elicitation 구현
```python
@mcp.tool()
async def create_task_session(
    task_name: str,
    description: str,
    ctx: Context
) -> Dict[str, Any]:
    """작업 세션 생성 with Context"""
    
    session_id = f"task_{datetime.now().timestamp()}"
    await ctx.info(f"새 작업 세션 생성 중: {task_name}")
    
    # 사용자에게 작업 설정 요청
    config_result = await ctx.elicit(
        message=f"'{task_name}' 작업의 설정을 구성해주세요",
        schema=TaskConfiguration
    )
    
    if config_result.action != "accept" or not config_result.data:
        await ctx.warning("작업 설정이 취소되었습니다")
        return {"status": "cancelled", "reason": "사용자가 설정을 취소함"}
    
    config = config_result.data
    
    # 세션 데이터 저장 (JSON 직렬화를 위해 model_dump() 사용)
    task_sessions[session_id] = {
        "id": session_id,
        "name": task_name,
        "description": description,
        "config": config.model_dump(),  # 중요: Pydantic 모델을 dict로 변환
        "status": "initialized",
        "created_at": datetime.now().isoformat(),
        "logs": [],
        "progress": 0
    }
    
    await ctx.info(f"작업 세션 생성 완료: {session_id}")
    
    # 리소스 목록 변경 알림
    await ctx.session.send_resource_list_changed()
    
    return {
        "session_id": session_id,
        "config": config,
        "message": f"작업 '{task_name}'이 생성되었습니다"
    }
```

#### 3. 진행 상황 보고 구현
```python
@mcp.tool()
async def execute_task(
    session_id: str,
    ctx: Context
) -> Dict[str, Any]:
    """작업 실행 with 상세한 진행 상황 보고"""
    
    if session_id not in task_sessions:
        await ctx.error(f"세션을 찾을 수 없습니다: {session_id}")
        return {"status": "error", "message": "세션이 존재하지 않습니다"}
    
    session = task_sessions[session_id]
    await ctx.info(f"작업 실행 시작: {session['name']}")
    
    steps = [
        ("초기화", 0.1),
        ("데이터 로드", 0.3),
        ("데이터 검증", 0.5),
        ("처리 실행", 0.8),
        ("결과 저장", 0.95),
        ("완료", 1.0)
    ]
    
    session['status'] = "running"
    
    for step_name, progress in steps:
        # 진행 상황 업데이트
        await ctx.report_progress(
            progress=progress,
            total=1.0,
            message=f"{step_name} 진행 중..."
        )
        
        # 세션 진행률 업데이트
        session['progress'] = progress * 100
        session['logs'].append({
            "timestamp": datetime.now().isoformat(),
            "step": step_name,
            "progress": progress
        })
        
        # 디버그 로그
        await ctx.debug(f"[{session_id}] {step_name} - {progress:.0%}")
        
        await asyncio.sleep(1)
        
        # 조건부 경고 (config는 이제 dict임)
        if step_name == "데이터 검증" and session['config']['priority'] == "high":
            await ctx.warning("고우선순위 작업 - 추가 검증 수행 중")
            await asyncio.sleep(0.5)
    
    session['status'] = "completed"
    session['completed_at'] = datetime.now().isoformat()
    
    # 완료 알림 (config는 이제 dict임)
    if session['config']['notify_on_complete']:
        await ctx.info(f"✅ 작업 완료: {session['name']}")
    
    return {
        "status": "success",
        "session_id": session_id,
        "execution_time": "6초",
        "logs": session['logs']
    }
```

## 클라이언트 구현: test-advanced-context.py

완전한 클라이언트 구현에는 다음 요소들이 포함됩니다:

### 1. Elicitation 핸들러
```python
async def elicitation_handler(context, params):
    """Advanced Context 테스트용 Elicitation 핸들러"""
    print(f"\n🤖 Elicitation 요청:")
    print(f"메시지: {params.message}")
    
    # 작업 설정 요청
    if "작업의 설정을 구성해주세요" in params.message:
        print("작업 설정을 구성합니다...")
        
        try:
            priority = input("작업 우선순위를 선택하세요 (low/medium/high) [medium]: ").strip()
            if not priority:
                priority = "medium"
        except EOFError:
            print("자동 기본값 사용: medium")
            priority = "medium"
        
        # 나머지 입력들도 EOF 처리...
        
        response_data = {
            "priority": priority,
            "notify_on_complete": notify_on_complete,
            "max_retries": max_retries
        }
        
        print(f"📝 작업 설정: {response_data}")
        return types.ElicitResult(action="accept", content=response_data)
    
    # 데이터 처리 옵션 요청
    elif "데이터 처리 옵션을 선택해주세요" in params.message:
        # 비슷한 처리 로직...
        return types.ElicitResult(action="accept", content=response_data)
    
    else:
        print("📝 기본 응답: 취소")
        return types.ElicitResult(action="cancel")
```

### 2. 로그 수집기와 알림 핸들러
```python
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
            print(f"🔔 알림: {type(message).__name__}")
```

### 3. 클라이언트 세션 설정
```python
async with ClientSession(
    read,
    write,
    logging_callback=log_collector,
    message_handler=notification_handler,
    elicitation_callback=elicitation_handler  # 중요: elicitation 콜백 추가
) as session:
    # 세션 초기화
    await session.initialize()
    
    # 도구 호출
    result = await session.call_tool(
        "create_task_session",
        arguments={
            "task_name": "데이터 분석 작업",
            "description": "대용량 로그 파일 분석"
        }
    )
```

## 중요한 수정사항과 문제 해결

### 1. Elicitation 결과 접근 방법
```python
# ❌ 잘못된 방법
if config_result.action != "accept" or not config_result.content:
    # 'content' 속성은 존재하지 않음

# ✅ 올바른 방법
if config_result.action != "accept" or not config_result.data:
    # 'data' 속성이 정확함
```

### 2. Pydantic 모델 JSON 직렬화
```python
# ❌ 잘못된 방법
task_sessions[session_id] = {
    "config": config,  # Pydantic 모델은 JSON 직렬화 불가
}

# ✅ 올바른 방법
task_sessions[session_id] = {
    "config": config.model_dump(),  # 딕셔너리로 변환
}
```

### 3. 변환된 딕셔너리 접근
```python
# config가 딕셔너리로 저장된 후:
if session['config']['priority'] == "high":  # 딕셔너리 접근
    await ctx.warning("고우선순위 작업")

if session['config']['notify_on_complete']:  # 딕셔너리 접근
    await ctx.info("✅ 작업 완료")
```

### 4. EOF 오류 처리
```python
try:
    priority = input("작업 우선순위를 선택하세요: ").strip()
except EOFError:
    print("자동 기본값 사용: medium")
    priority = "medium"
```

### 5. ElicitResult 생성 시 올바른 파라미터
```python
# 클라이언트에서 ElicitResult 생성할 때
return types.ElicitResult(action="accept", content=response_data)

# 서버에서 결과 접근할 때
config = config_result.data  # 'data' 속성 사용
```

## 실제 테스트 결과

다음은 완전히 작동하는 구현의 테스트 결과입니다:

```
🚀 Context 고급 기능 테스트 시작
============================================================
✅ 서버에 연결되었습니다.

📋 사용 가능한 도구: 4개
  - create_task_session
  - execute_task
  - process_data_batch
  - monitor_system

============================================================
🧪 작업 세션 생성 및 실행 테스트
============================================================

1️⃣ 작업 세션 생성
ℹ️ [INFO] 새 작업 세션 생성 중: 데이터 분석 작업

🤖 Elicitation 요청:
메시지: '데이터 분석 작업' 작업의 설정을 구성해주세요
작업 설정을 구성합니다...
자동 기본값 사용: medium
자동 기본값 사용: 알림 받기
자동 기본값 사용: 3
📝 작업 설정: {'priority': 'medium', 'notify_on_complete': True, 'max_retries': 3}

ℹ️ [INFO] 작업 세션 생성 완료: task_1752589370.125551
✅ 세션 생성됨: task_1752589370.125551
   설정: {'priority': 'medium', 'notify_on_complete': True, 'max_retries': 3}

2️⃣ 작업 실행
ℹ️ [INFO] 작업 실행 시작: 데이터 분석 작업
🔍 [DEBUG] [task_1752589370.125551] 초기화 - 10%
🔍 [DEBUG] [task_1752589370.125551] 데이터 로드 - 30%
🔍 [DEBUG] [task_1752589370.125551] 데이터 검증 - 50%
🔍 [DEBUG] [task_1752589370.125551] 처리 실행 - 80%
🔍 [DEBUG] [task_1752589370.125551] 결과 저장 - 95%
🔍 [DEBUG] [task_1752589370.125551] 완료 - 100%
ℹ️ [INFO] ✅ 작업 완료: 데이터 분석 작업
✅ 작업 완료: success
   실행 시간: 6초

3️⃣ 세션 정보 조회
📄 세션 정보:
{
  "session": {
    "id": "task_1752589370.125551",
    "name": "데이터 분석 작업",
    "description": "대용량 로그 파일 분석",
    "config": {
      "priority": "medium",
      "notify_on_complete": true,
      "max_retries": 3
    },
    "status": "completed",
    "created_at": "2025-07-15T23:22:50.127270",
    "logs": [
      {
        "timestamp": "2025-07-15T23:22:50.130740",
        "step": "초기화",
        "progress": 0.1
      },
      // ... 더 많은 로그
    ],
    "progress": 100.0,
    "completed_at": "2025-07-15T23:22:56.139211"
  }
}

============================================================
🧪 배치 데이터 처리 테스트
============================================================
ℹ️ [INFO] 5개 항목 처리 준비

🤖 Elicitation 요청:
메시지: 데이터 처리 옵션을 선택해주세요
자동 기본값 사용: json
자동 기본값 사용: 메타데이터 포함
자동 기본값 사용: 압축 안함
📝 처리 옵션: {'format': 'json', 'include_metadata': True, 'compression': False}

ℹ️ [INFO] 배치 처리 완료: 5개 성공

📊 처리 결과:
   성공: 5개
   실패: 0개
   형식: json

============================================================
🧪 시스템 모니터링 테스트
============================================================
ℹ️ [INFO] 5초 동안 시스템 모니터링 시작
❌ [ERROR] 🚨 메모리 사용률 위험: 52%
ℹ️ [INFO] 모니터링 완료

📈 모니터링 요약:
   평균 CPU: 24.0%
   평균 메모리: 46.0%
   최대 CPU: 28%
   최대 메모리: 52%

============================================================
📊 최종 통계
============================================================
총 로그 메시지: 15개
총 알림: 16개

로그 레벨별 통계:
  debug: 6개
  error: 1개
  info: 8개
```

## 정리

Context는 MCP 서버를 더욱 강력하고 사용자 친화적으로 만드는 핵심 기능입니다. 로깅, 진행 상황 보고, 사용자 상호작용 등을 통해 풍부한 사용자 경험을 제공할 수 있습니다.

### 주요 장점:
- **실시간 피드백 제공**: 진행 상황과 상태를 실시간으로 보고
- **디버깅 용이성**: 다단계 로깅으로 문제 추적 용이
- **사용자와의 상호작용**: Elicitation을 통한 동적 입력 수집
- **세션 상태 관리**: 복잡한 작업 세션을 체계적으로 관리
- **리소스 동기화**: 동적 리소스 변경 사항 실시간 반영

### 구현 시 핵심 포인트:
1. **올바른 속성 접근**: `result.data` (not `result.content`)
2. **Pydantic 모델 직렬화**: `model.model_dump()` 사용
3. **EOF 오류 처리**: 비대화형 환경에서의 입력 처리
4. **적절한 콜백 설정**: `elicitation_callback` 필수 설정
5. **비동기 함수 사용**: 모든 Context 메서드는 `await` 필요

Context를 적절히 활용하면 단순한 도구를 넘어 완전한 애플리케이션 수준의 기능을 제공할 수 있습니다. 이 가이드의 구현 예제를 참고하여 안정적이고 기능이 풍부한 MCP 서버를 구축하세요. 