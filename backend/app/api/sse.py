"""SSE 端点 - 服务器发送事件"""
import asyncio
import json
from typing import AsyncGenerator, Optional
from fastapi import APIRouter, Request, Depends, HTTPException
from starlette.responses import StreamingResponse
from app.config import get_settings
from app.models import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/sse", tags=["sse"])

# 全局事件字典，用于存储不同用户的事件队列
event_queues: dict[str, asyncio.Queue] = {}

async def event_generator(task_id: str) -> AsyncGenerator[str, None]:
    """SSE 事件生成器"""
    queue = event_queues.get(task_id)
    if not queue:
        raise HTTPException(status_code=404, detail="Task not found")
    
    while True:
        try:
            # 等待事件，超时后继续检查
            try:
                event = await asyncio.wait_for(queue.get(), timeout=30.0)
                yield f"data: {json.dumps(event)}\n\n"
            except asyncio.TimeoutError:
                # 发送心跳保活
                yield ": keep-alive\n\n"
                continue
        except Exception as e:
            print(f"Event generator error: {e}")
            break

@router.get("/{task_id}")
async def sse_endpoint(task_id: str):
    """SSE 连接端点"""
    if task_id not in event_queues:
        event_queues[task_id] = asyncio.Queue()
    
    return StreamingResponse(
        event_generator(task_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

async def send_event(task_id: str, event_type: str, data: dict):
    """发送 SSE 事件"""
    if task_id not in event_queues:
        event_queues[task_id] = asyncio.Queue()
    
    event = {
        "type": event_type,
        "data": data,
        "timestamp": asyncio.get_event_loop().time()
    }
    
    await event_queues[task_id].put(event)

def cleanup_task(task_id: str):
    """清理任务事件队列"""
    if task_id in event_queues:
        del event_queues[task_id]
