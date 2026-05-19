"""任务服务模块"""
from datetime import datetime
from typing import Dict, Optional

# 简单的内存存储
_task_db: Dict[str, Dict] = {}


def create_generation_task(
    task_id: str,
    file_id: str,
    user_prompt: str,
    model_config: Optional[Dict] = None
) -> Dict:
    """创建生成任务"""
    now = datetime.now()
    task = {
        "task_id": task_id,
        "file_id": file_id,
        "user_prompt": user_prompt,
        "model_config": model_config or {},
        "status": "pending",
        "step": 0,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
    }
    _task_db[task_id] = task
    return task


def get_task_status(task_id: str) -> Dict:
    """获取任务状态"""
    task = _task_db.get(task_id)
    if not task:
        raise ValueError("Task not found")
    return task


def get_task_result(task_id: str) -> Optional[Dict]:
    """获取任务结果（真实数据）"""
    task = _task_db.get(task_id)
    if not task:
        return None
    return {
        "task_id": task_id,
        "status": task.get("status", "unknown"),
        "user_prompt": task.get("user_prompt", ""),
        "generated_prompt": task.get("generated_prompt"),
        "dashboard_spec": task.get("dashboard_spec"),
        "created_at": task.get("created_at"),
    }


def update_task_status(task_id: str, status: str, step: int, message: str, extra: Optional[Dict] = None):
    """更新任务状态，extra 中的字段会合并写入任务字典"""
    task = _task_db.get(task_id)
    if task:
        task["status"] = status
        task["step"] = step
        task["message"] = message
        if extra:
            task.update(extra)
        task["updated_at"] = datetime.now().isoformat()


def get_task_result_data(task_id: str) -> Optional[Dict]:
    """获取任务结果数据"""
    return _task_db.get(task_id)
