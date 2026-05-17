"""任务查询 API"""
from fastapi import APIRouter, HTTPException

from app.services.task_service import get_task_status, get_task_result


router = APIRouter(prefix="/task", tags=["task"])


@router.get("/{task_id}")
async def get_task(task_id: str):
    """获取任务状态"""
    try:
        status = get_task_status(task_id)
        return status
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"任务不存在: {str(e)}")


@router.get("/{task_id}/result")
async def get_result(task_id: str):
    """获取任务结果"""
    try:
        result = get_task_result(task_id)
        if not result:
            raise HTTPException(status_code=404, detail="结果不存在")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取结果失败: {str(e)}")
