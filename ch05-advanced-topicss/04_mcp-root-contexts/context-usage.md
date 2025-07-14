# MCP Context 사용법

## Context란?

Context는 MCP 도구(tool)와 리소스(resource)에서 사용할 수 있는 특별한 객체로, 다음과 같은 기능을 제공합니다:

- **로깅**: 다양한 레벨의 로그 메시지 전송
- **진행 상황 보고**: 작업 진행률을 클라이언트에 실시간 전달
- **사용자 입력 요청**: 추가 정보나 선택을 요청
- **세션 접근**: 현재 세션 정보 및 기능 사용

## Context 사용 방법

### 1. Context 임포트 및 파라미터 추가

```python
from mcp.server.fastmcp import FastMCP, Context

@mcp.tool()
async def my_tool(param: str, ctx: Context) -> str:
    # Context를 사용하는 도구
    pass
```

**중요**: Context를 사용하려면 함수는 반드시 `async`여야 합니다.

### 2. 로깅 기능

Context는 다양한 레벨의 로그를 제공합니다:

```python
# 디버그 정보 (개발 시 유용)
await ctx.debug("디버그 메시지")

# 일반 정보
await ctx.info("작업을 시작합니다")

# 경고
await ctx.warning("주의가 필요한 상황입니다")

# 에러 (심각한 문제)
await ctx.error("오류가 발생했습니다")
```

### 3. 진행 상황 보고

긴 작업의 진행 상황을 실시간으로 보고할 수 있습니다:

```python
@mcp.tool()
async def long_task(items: list[str], ctx: Context) -> str:
    total = len(items)
    
    for idx, item in enumerate(items):
        # 진행률 계산 및 보고
        progress = (idx + 1) / total
        await ctx.report_progress(
            progress=progress,
            total=1.0,
            message=f"{item} 처리 중... ({idx + 1}/{total})"
        )
        
        # 실제 작업 수행
        await process_item(item)
    
    return "완료!"
```

### 4. 사용자 입력 요청 (Elicitation)

작업 중 사용자에게 추가 정보를 요청할 수 있습니다:

```python
from pydantic import BaseModel, Field

class UserChoice(BaseModel):
    option: str = Field(description="선택한 옵션")
    confirm: bool = Field(description="확인 여부")

@mcp.tool()
async def interactive_tool(ctx: Context) -> str:
    # 사용자에게 선택 요청
    result = await ctx.elicit(
        message="어떤 옵션을 선택하시겠습니까?",
        schema=UserChoice
    )
    
    if result.action == "accept" and result.data:
        if result.data.confirm:
            return f"선택한 옵션: {result.data.option}"
        else:
            return "취소되었습니다"
    
    return "사용자가 응답하지 않았습니다"
```

### 5. 세션 접근

Context를 통해 현재 세션에 접근할 수 있습니다:

```python
@mcp.tool()
async def session_info(ctx: Context) -> dict:
    # 세션을 통한 추가 기능 사용
    # 예: 리소스 변경 알림
    await ctx.session.send_resource_list_changed()
    
    return {"status": "리소스 목록이 업데이트되었습니다"}
```

## 실행 예제

### 서버 실행

```bash
# Context를 사용하는 서버 실행
uv run python ch01/02_weather-server-with-context.py
```

### 클라이언트에서 테스트

```bash
# MCP Inspector로 테스트
uv run mcp dev ch01/02_weather-server-with-context.py

# 또는 Claude Desktop에 설치
uv run mcp install ch01/02_weather-server-with-context.py
```

## Context 사용 시 주의사항

1. **비동기 함수 필수**: Context를 사용하는 함수는 반드시 `async def`로 선언해야 합니다.
2. **에러 처리**: Context 메서드 호출 시 에러가 발생할 수 있으므로 적절한 에러 처리가 필요합니다.
3. **클라이언트 지원**: 모든 클라이언트가 모든 Context 기능을 지원하는 것은 아닙니다.

## 활용 예시

### 파일 처리 도구
```python
@mcp.tool()
async def process_files(
    file_paths: list[str], 
    ctx: Context
) -> dict:
    """여러 파일을 처리하며 진행 상황 보고"""
    
    processed = []
    errors = []
    
    for idx, path in enumerate(file_paths):
        try:
            await ctx.info(f"파일 처리 중: {path}")
            
            # 진행률 보고
            await ctx.report_progress(
                progress=(idx + 1) / len(file_paths),
                total=1.0,
                message=f"{path} 처리 중..."
            )
            
            # 실제 파일 처리 로직
            result = await process_file(path)
            processed.append(result)
            
        except Exception as e:
            await ctx.error(f"파일 처리 실패: {path} - {str(e)}")
            errors.append({"file": path, "error": str(e)})
    
    return {
        "processed": len(processed),
        "errors": len(errors),
        "details": {
            "successful": processed,
            "failed": errors
        }
    }
```

### 데이터 분석 도구
```python
@mcp.tool()
async def analyze_data(
    dataset_name: str,
    options: dict,
    ctx: Context
) -> dict:
    """데이터셋 분석 with 상세 로깅"""
    
    await ctx.info(f"데이터셋 '{dataset_name}' 분석 시작")
    await ctx.debug(f"분석 옵션: {options}")
    
    # 단계별 진행
    steps = ["로딩", "전처리", "분석", "결과 생성"]
    
    for idx, step in enumerate(steps):
        await ctx.report_progress(
            progress=(idx + 1) / len(steps),
            total=1.0,
            message=f"{step} 단계 진행 중..."
        )
        
        # 각 단계 시뮬레이션
        await asyncio.sleep(1)
        
        if step == "분석" and options.get("deep_analysis"):
            await ctx.warning("심층 분석은 시간이 오래 걸릴 수 있습니다")
    
    await ctx.info("분석 완료!")
    
    return {
        "dataset": dataset_name,
        "results": {
            "rows": 1000,
            "columns": 20,
            "insights": ["인사이트 1", "인사이트 2"]
        }
    }
```

## 정리

Context는 MCP 도구를 더욱 강력하고 사용자 친화적으로 만들어주는 핵심 기능입니다. 로깅, 진행 상황 보고, 사용자 상호작용 등을 통해 더 나은 사용자 경험을 제공할 수 있습니다. 