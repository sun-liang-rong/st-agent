"""报表生成 API"""
import os
import uuid
import glob
import pandas as pd
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import get_db
from app.services.task_service import create_generation_task, update_task_status, get_task_result_data
from app.services.ai_service import aiservice
from app.services.history_service import create_history
from app.api.sse import send_event
from app.utils.common import create_camel_response


router = APIRouter(prefix="/generate", tags=["generate"])
settings = get_settings()


class GenerateRequest(BaseModel):
    file_id: str = Field(..., description="文件 ID", alias="fileId")
    user_prompt: str = Field(..., description="用户分析需求", alias="userPrompt")
    options: Optional[dict] = Field(None, description="模型配置")
    
    class Config:
        validate_by_name = True


@router.post("")
async def generate_report(request: GenerateRequest, db: Session = Depends(get_db)):
    """发起报表生成请求"""
    if not request.file_id or not request.user_prompt:
        raise HTTPException(status_code=400, detail="缺少必要参数")
    
    try:
        task_id = str(uuid.uuid4())
        task = create_generation_task(
            task_id=task_id,
            file_id=request.file_id,
            user_prompt=request.user_prompt,
            model_config=request.options
        )
        
        return create_camel_response({
            "task_id": task_id,
            "status": "processing",
            "message": "任务已创建，正在处理...",
            "created_at": task.get("created_at", "")
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建任务失败: {str(e)}")


@router.post("/{task_id}/execute")
async def execute_report_generation(task_id: str, db: Session = Depends(get_db)):
    """执行报表生成"""
    try:
        task = get_task_result_data(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        await send_event(task_id, "progress", {
            "step": 1,
            "total": 4,
            "message": "正在读取文件数据...",
            "status": "processing"
        })
        
        update_task_status(task_id, "processing", 1, "正在读取文件数据...")
        
        # 查找实际文件（支持 .xlsx / .xls / .csv）
        file_dir = "uploads"
        file_id = task['file_id']
        matches = glob.glob(os.path.join(file_dir, f"{file_id}.*"))
        if not matches:
            raise HTTPException(status_code=404, detail="文件不存在")
        file_path = matches[0]
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # 根据扩展名选择读取方式
        if file_ext == '.csv':
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        # 完整数据解析：全部行数据 + 统计摘要
        full_data = df.to_string()
        MAX_DATA_LEN = 50000  # 最多发 5 万字符给大模型
        if len(full_data) > MAX_DATA_LEN:
            # 超大文件：发统计摘要 + 头尾各 50 行
            stats = df.describe(include='all').to_string()
            head = df.head(50).to_string()
            tail = df.tail(50).to_string()
            file_data = (
                f"总行数: {len(df)}, 总列数: {len(df.columns)}\n"
                f"列名: {list(df.columns)}\n\n"
                f"--- 统计摘要 ---\n{stats}\n\n"
                f"--- 前50行 ---\n{head}\n\n"
                f"--- 后50行 ---\n{tail}"
            )
        else:
            file_data = full_data
        
        file_name = os.path.basename(file_path)
        
        await send_event(task_id, "progress", {
            "step": 2,
            "total": 4,
            "message": "正在分析数据...",
            "status": "processing"
        })
        
        update_task_status(task_id, "processing", 2, "正在分析数据...")
        
        generated_prompt = await aiservice.analyze_file_and_generate_prompt(
            file_data=file_data,
            user_prompt=task["user_prompt"],
            file_name=file_name
        )
        
        await send_event(task_id, "prompt_generated", {
            "prompt": generated_prompt,
            "message": "数据分析完成"
        })
        
        await send_event(task_id, "progress", {
            "step": 3,
            "total": 4,
            "message": "正在生成图表...",
            "status": "processing"
        })
        
        update_task_status(task_id, "processing", 3, "正在生成图表...")
        
        image_url = await aiservice.generate_image(generated_prompt)
        
        # 保存历史记录
        try:
            create_history(
                db=db,
                file_id=task["file_id"],
                file_name=file_name,
                user_prompt=task["user_prompt"],
                generated_prompt=generated_prompt,
                image_url=image_url,
            )
        except Exception as e:
            print(f"保存历史记录失败: {e}")

        await send_event(task_id, "progress", {
            "step": 4,
            "total": 4,
            "message": "生成完成",
            "status": "completed"
        })
        
        await send_event(task_id, "complete", {
            "generated_prompt": generated_prompt,
            "image_url": image_url
        })
        
        update_task_status(task_id, "completed", 4, "生成完成")
        
        return create_camel_response({
            "task_id": task_id,
            "status": "completed",
            "generated_prompt": generated_prompt,
            "image_url": image_url
        })
    
    except Exception as e:
        await send_event(task_id, "error", {
            "message": f"生成失败: {str(e)}"
        })
        update_task_status(task_id, "failed", 0, f"生成失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")
