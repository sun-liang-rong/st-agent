"""通用工具函数"""
import re
from typing import Any
from fastapi.responses import JSONResponse
from pydantic import BaseModel


def snake_to_camel(snake_str: str) -> str:
    """
    将下划线命名转换为驼峰命名
    """
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def convert_dict_to_camel(data: Any) -> Any:
    """
    递归将字典的键从下划线命名转换为驼峰命名
    """
    if isinstance(data, dict):
        return {snake_to_camel(k): convert_dict_to_camel(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_dict_to_camel(item) for item in data]
    else:
        return data


class CamelModel(BaseModel):
    """
    自动转换为驼峰命名的 Pydantic 基类
    """
    class Config:
        populate_by_name = True
        
        @classmethod
        def alias_generator(cls, string: str) -> str:
            return snake_to_camel(string)


def create_camel_response(data: Any, status_code: int = 200) -> JSONResponse:
    """
    创建响应（自动将键名转换为驼峰格式）
    """
    return JSONResponse(content=convert_dict_to_camel(data), status_code=status_code)
