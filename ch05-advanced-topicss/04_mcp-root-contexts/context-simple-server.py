#!/usr/bin/env python3
"""
Context 기능을 보여주는 간단한 데모 서버
- Elicitation 없이 기본 Context 기능만 사용
"""
from mcp.server.fastmcp import FastMCP, Context
import asyncio
from datetime import datetime
from typing import Dict, List, Any
import json

# FastMCP 서버 생성
mcp = FastMCP(
    name="Simple Context Demo",
    version="1.0.0",
    description="Context 기본 기능 데모"
)

# 데이터 저장소
tasks = {}

@mcp.tool()
async def simple_task(name: str, duration: int, ctx: Context) -> Dict[str, Any]:
    """간단한 작업 실행 with Context 로깅"""
    task_id = f"task_{datetime.now().timestamp()}"
    
    # 정보 로그
    await ctx.info(f"작업 시작: {name}")
    
    # 디버그 로그
    await ctx.debug(f"작업 ID: {task_id}, 예상 시간: {duration}초")
    
    # 진행 상황 보고
    for i in range(duration):
        progress = (i + 1) / duration
        await ctx.report_progress(
            progress=progress,
            total=1.0,
            message=f"{name} - {i+1}/{duration}초 경과"
        )
        # await ctx.debug(f"progress: {progress*100:.0f}%")
        await asyncio.sleep(1)
    
    # 완료 로그
    await ctx.info(f"작업 완료: {name}")
    
    # 결과 저장
    tasks[task_id] = {
        "id": task_id,
        "name": name,
        "duration": duration,
        "completed_at": datetime.now().isoformat()
    }
    
    return {
        "task_id": task_id,
        "status": "completed",
        "message": f"'{name}' 작업이 {duration}초 만에 완료되었습니다"
    }

@mcp.tool()
async def batch_process(items: List[str], ctx: Context) -> Dict[str, Any]:
    """배치 처리 with 진행 상황"""
    await ctx.info(f"배치 처리 시작: {len(items)}개 항목")
    
    processed = []
    errors = []
    
    for idx, item in enumerate(items):
        try:
            # 진행 상황 보고
            progress = (idx + 1) / len(items)
            await ctx.report_progress(
                progress=progress,
                total=1.0,
                message=f"처리 중: {item}"
            )
            # 처리 시뮬레이션
            await asyncio.sleep(0.5)
            
            # 가끔 경고 발생
            if idx == 2:
                await ctx.warning(f"항목 '{item}'에서 경고 발생")
            
            processed.append({
                "item": item,
                "processed_at": datetime.now().isoformat()
            })
            
            # await ctx.debug(f"progress: {progress*100:.0f}%")
            # await ctx.debug(f"항목 처리 완료: {item}")
        except Exception as e:
            await ctx.error(f"항목 처리 실패: {item} - {str(e)}")
            errors.append({"item": item, "error": str(e)})
    
    await ctx.info(f"배치 처리 완료: 성공 {len(processed)}개, 실패 {len(errors)}개")
    
    return {
        "total": len(items),
        "processed": len(processed),
        "failed": len(errors),
        "items": processed
    }

@mcp.tool()
async def monitor_metrics(
    seconds: int,
    ctx: Context
) -> Dict[str, Any]:
    """메트릭 모니터링 with 로그 레벨"""
    
    await ctx.info(f"모니터링 시작 ({seconds}초)")
    
    metrics = []
    
    for i in range(seconds):
        # 메트릭 생성
        cpu = 40 + (i * 5) % 40
        memory = 30 + (i * 3) % 30
        
        metric = {
            "time": i + 1,
            "cpu": cpu,
            "memory": memory
        }
        metrics.append(metric)
        
        # 진행 상황
        progress = (i + 1) / seconds
        await ctx.report_progress(
            progress=progress,
            total=1.0,
            message=f"CPU: {cpu}%, MEM: {memory}%"
        )
        # await ctx.debug(f"progress: {progress*100:.0f}%")
        
        # 조건에 따른 로그 레벨
        if cpu > 50:
            await ctx.error(f"🚨 CPU 사용률 위험: {cpu}%")
        elif cpu > 40:
            await ctx.warning(f"⚠️ CPU 사용률 높음: {cpu}%")
        else:
            await ctx.debug(f"CPU 정상: {cpu}%")
        
        await asyncio.sleep(1)
    
    await ctx.info("모니터링 완료")
    
    return {
        "duration": seconds,
        "metrics": metrics,
        "summary": {
            "avg_cpu": sum(m['cpu'] for m in metrics) / len(metrics),
            "avg_memory": sum(m['memory'] for m in metrics) / len(metrics),
            "max_cpu": max(m['cpu'] for m in metrics),
            "max_memory": max(m['memory'] for m in metrics)
        }
    }

# 리소스
@mcp.resource("tasks://list")
def list_tasks() -> str:
    """작업 목록"""
    return json.dumps({
        "tasks": list(tasks.values()),
        "count": len(tasks)
    }, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    mcp.run() 