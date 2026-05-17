"""任务服务模块（模拟）"""
import time
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
    """获取任务状态（模拟进度）"""
    task = _task_db.get(task_id, None)
    if not task:
        raise ValueError("Task not found")
    
    # 模拟进度
    elapsed = time.time() - datetime.fromisoformat(task["created_at"]).timestamp()
    if elapsed < 2:
        task["status"] = "processing"
        task["step"] = 1
        task["message"] = "正在分析数据..."
    elif elapsed < 5:
        task["status"] = "processing"
        task["step"] = 2
        task["message"] = "正在生成提示词..."
    elif elapsed < 8:
        task["status"] = "processing"
        task["step"] = 3
        task["message"] = "正在生成报表..."
    else:
        task["status"] = "completed"
        task["step"] = 4
        task["message"] = "生成完成"
    
    task["updated_at"] = datetime.now().isoformat()
    _task_db[task_id] = task
    return task


def get_task_result(task_id: str) -> Optional[Dict]:
    """获取任务结果（模拟）"""
    task = _task_db.get(task_id, None)
    if not task:
        return None
    
    return {
        "task_id": task_id,
        "status": "completed",
        "user_prompt": task["user_prompt"],
        "generated_prompt": "生成的提示词内容...",
        "report_url": "/generated/sample-report.png",
        "created_at": task["created_at"],
    }


def update_task_status(task_id: str, status: str, step: int, message: str):
    """更新任务状态"""
    task = _task_db.get(task_id)
    if task:
        task["status"] = status
        task["step"] = step
        task["message"] = message
        task["updated_at"] = datetime.now().isoformat()
        _task_db[task_id] = task


def get_task_result_data(task_id: str) -> Optional[Dict]:
    """获取任务结果数据"""
    return _task_db.get(task_id)
