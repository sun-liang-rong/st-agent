"""通用工具函数"""
import re
from datetime import datetime, date
from decimal import Decimal
from typing import Any
from fastapi.responses import JSONResponse
from pydantic import BaseModel


def snake_to_camel(snake_str: str) -> str:
    """将下划线命名转换为驼峰命名"""
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def _to_serializable(obj: Any) -> Any:
    """将 ORM 对象和非 JSON 类型转为可序列化值"""
    # SQLAlchemy ORM 对象
    if hasattr(obj, '__dict__') and hasattr(obj, '_sa_instance_state'):
        return {k: _to_serializable(v) for k, v in obj.__dict__.items() if not k.startswith('_')}
    # datetime / date
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, date):
        return obj.isoformat()
    # Decimal
    if isinstance(obj, Decimal):
        return float(obj)
    return obj


def convert_dict_to_camel(data: Any) -> Any:
    """递归将字典的键从下划线命名转换为驼峰命名"""
    data = _to_serializable(data)
    if isinstance(data, dict):
        return {snake_to_camel(k): convert_dict_to_camel(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_dict_to_camel(item) for item in data]
    else:
        return data


def create_camel_response(data: Any, status_code: int = 200) -> JSONResponse:
    """创建驼峰命名的 JSON 响应"""
    camel_data = convert_dict_to_camel(data)
    return JSONResponse(content=camel_data, status_code=status_code)