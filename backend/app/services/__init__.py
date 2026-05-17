"""服务模块初始化"""
from .task_service import create_generation_task, get_task_status, get_task_result

__all__ = ["create_generation_task", "get_task_status", "get_task_result"]
