#!/usr/bin/env python3
"""
Context 고급 기능을 활용하는 MCP 서버 예제
- 세션 관리와 Context 연동
- 진행 상황 추적
- 사용자 상호작용
- 리소스 업데이트 알림
"""
from mcp.server.fastmcp import FastMCP, Context
from mcp.types import TextContent, ImageContent
from pydantic import BaseModel, Field
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
import json
import base64

# FastMCP 서버 생성
mcp = FastMCP(
    name="Advanced Context Demo",
    version="1.0.0",
    description="Context의 고급 기능을 보여주는 데모 서버"
)

# 데이터 저장소 (메모리 기반)
task_sessions: Dict[str, Dict[str, Any]] = {}
resource_data: Dict[str, Any] = {}

# 사용자 입력 스키마들
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

@mcp.tool()
async def create_task_session(
    task_name: str,
    description: str,
    ctx: Context
) -> Dict[str, Any]:
    """작업 세션 생성 with Context"""
    
    # 세션 ID 생성
    session_id = f"task_{datetime.now().timestamp()}"
    
    await ctx.info(f"새 작업 세션 생성 중: {task_name}")
    
    # 사용자에게 작업 설정 요청
    config_result = await ctx.elicit(
        message=f"'{task_name}' 작업의 설정을 구성해주세요",
        schema=TaskConfiguration
    )
    
    # print(f"config_result: {config_result}")
    if config_result.action != "accept" or not config_result.data:
        await ctx.warning("작업 설정이 취소되었습니다")
        return {"status": "cancelled", "reason": "사용자가 설정을 취소함"}
    
    config = config_result.data
    
    # 세션 데이터 저장
    task_sessions[session_id] = {
        "id": session_id,
        "name": task_name,
        "description": description,
        "config": config.model_dump(),  # Convert Pydantic model to dict for JSON serialization
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
    
    # 작업 단계들
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
        
        # 시뮬레이션 딜레이
        await asyncio.sleep(1)
        
        # 특정 단계에서 경고 발생 시뮬레이션
        if step_name == "데이터 검증" and session['config']['priority'] == "high":
            await ctx.warning("고우선순위 작업 - 추가 검증 수행 중")
            await asyncio.sleep(0.5)
    
    session['status'] = "completed"
    session['completed_at'] = datetime.now().isoformat()
    
    # 완료 알림
    if session['config']['notify_on_complete']:
        await ctx.info(f"✅ 작업 완료: {session['name']}")
    
    return {
        "status": "success",
        "session_id": session_id,
        "execution_time": "6초",
        "logs": session['logs']
    }

@mcp.tool()
async def process_data_batch(
    data_items: List[str],
    ctx: Context
) -> Dict[str, Any]:
    """배치 데이터 처리 with 사용자 옵션"""
    
    await ctx.info(f"{len(data_items)}개 항목 처리 준비")
    
    # 처리 옵션 요청
    options_result = await ctx.elicit(
        message="데이터 처리 옵션을 선택해주세요",
        schema=DataProcessingOptions
    )
    
    if options_result.action != "accept" or not options_result.data:
        return {"status": "cancelled", "message": "처리가 취소되었습니다"}
    
    options = options_result.data
    
    processed_items = []
    errors = []
    
    for idx, item in enumerate(data_items):
        try:
            # 진행 상황 보고
            progress = (idx + 1) / len(data_items)
            await ctx.report_progress(
                progress=progress,
                total=1.0,
                message=f"항목 {idx + 1}/{len(data_items)} 처리 중: {item}"
            )
            
            # 처리 시뮬레이션
            await asyncio.sleep(0.5)
            
            # 처리 결과
            result = {
                "item": item,
                "processed": True,
                "timestamp": datetime.now().isoformat()
            }
            
            if options.include_metadata:
                result["metadata"] = {
                    "index": idx,
                    "size": len(item),
                    "format": options.format
                }
            
            processed_items.append(result)
            
        except Exception as e:
            await ctx.error(f"항목 처리 실패: {item} - {str(e)}")
            errors.append({"item": item, "error": str(e)})
    
    # 결과 포맷팅
    output = {
        "processed": len(processed_items),
        "failed": len(errors),
        "format": options.format,
        "items": processed_items
    }
    
    if errors:
        output["errors"] = errors
        await ctx.warning(f"{len(errors)}개 항목 처리 실패")
    
    await ctx.info(f"배치 처리 완료: {len(processed_items)}개 성공")
    
    return output

@mcp.tool()
async def monitor_system(
    duration_seconds: int,
    ctx: Context
) -> Dict[str, Any]:
    """시스템 모니터링 with 실시간 업데이트"""
    
    await ctx.info(f"{duration_seconds}초 동안 시스템 모니터링 시작")
    
    metrics = []
    
    for i in range(duration_seconds):
        # 메트릭 수집 (시뮬레이션)
        metric = {
            "timestamp": datetime.now().isoformat(),
            "cpu": 20 + (i * 2) % 30,
            "memory": 40 + (i * 3) % 20,
            "disk": 60 + (i % 10)
        }
        
        metrics.append(metric)
        
        # 실시간 상태 보고
        status_msg = f"CPU: {metric['cpu']}%, MEM: {metric['memory']}%, DISK: {metric['disk']}%"
        
        # 진행률과 함께 상태 보고
        await ctx.report_progress(
            progress=(i + 1) / duration_seconds,
            total=1.0,
            message=status_msg
        )
        
        # 임계값 체크
        if metric['cpu'] > 40:
            await ctx.warning(f"⚠️ CPU 사용률 높음: {metric['cpu']}%")
        
        if metric['memory'] > 50:
            await ctx.error(f"🚨 메모리 사용률 위험: {metric['memory']}%")
        
        await asyncio.sleep(1)
    
    await ctx.info("모니터링 완료")
    
    # 요약 통계
    avg_cpu = sum(m['cpu'] for m in metrics) / len(metrics)
    avg_mem = sum(m['memory'] for m in metrics) / len(metrics)
    
    return {
        "duration": duration_seconds,
        "metrics_collected": len(metrics),
        "summary": {
            "avg_cpu": round(avg_cpu, 2),
            "avg_memory": round(avg_mem, 2),
            "max_cpu": max(m['cpu'] for m in metrics),
            "max_memory": max(m['memory'] for m in metrics)
        },
        "metrics": metrics
    }

# 동적 리소스 (리소스는 Context를 지원하지 않음)
@mcp.resource("task://session/{session_id}")
def get_task_session(session_id: str) -> str:
    """작업 세션 정보 리소스"""
    
    if session_id not in task_sessions:
        return json.dumps({
            "error": "세션을 찾을 수 없습니다",
            "session_id": session_id
        }, indent=2, ensure_ascii=False)
    
    session = task_sessions[session_id]
    
    return json.dumps({
        "session": session,
        "accessed_at": datetime.now().isoformat()
    }, indent=2, ensure_ascii=False)

@mcp.resource("tasks://active")
def get_active_tasks() -> str:
    """활성 작업 목록"""
    
    active = [
        session for session in task_sessions.values()
        if session['status'] in ['initialized', 'running']
    ]
    
    return json.dumps({
        "active_tasks": len(active),
        "tasks": active,
        "timestamp": datetime.now().isoformat()
    }, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    mcp.run() 