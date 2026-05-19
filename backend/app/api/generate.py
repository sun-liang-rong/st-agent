"""报表生成 API"""
import os
import uuid
import glob
import pandas as pd
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Any
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import get_db
from app.services.task_service import create_generation_task, update_task_status, get_task_result_data
from app.services.ai_service import aiservice
from app.services.history_service import create_history
from app.api.sse import send_event, cleanup_task
from app.utils.common import create_camel_response


router = APIRouter(prefix="/generate", tags=["generate"])
settings = get_settings()


def _build_file_data(file_path: str) -> str:
    """读取文件并构建结构化数据摘要"""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.csv':
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)

    total_rows = len(df)
    columns = list(df.columns)

    # 构建结构化摘要
    col_summaries = []
    for col in columns:
        col_data = df[col]
        if pd.api.types.is_numeric_dtype(col_data):
            clean = col_data.dropna()
            info = f"  - {col} (数值)"
            if len(clean) > 0:
                info += f" [min={clean.min():.2f}, max={clean.max():.2f}, mean={clean.mean():.2f}, sum={clean.sum():.2f}]"
            col_summaries.append(info)
        elif pd.api.types.is_datetime64_any_dtype(col_data):
            col_summaries.append(f"  - {col} (日期)")
        else:
            unique = col_data.nunique()
            top_values = col_data.value_counts().head(10).index.tolist()
            col_summaries.append(f"  - {col} (分类, {unique}个值) top: {top_values}")

    # 取前 50 行数据样本
    sample = df.head(50).to_string(index=False)

    return (
        f"文件: {os.path.basename(file_path)}\n"
        f"总行数: {total_rows}, 总列数: {len(columns)}\n\n"
        f"列信息:\n" + "\n".join(col_summaries) + "\n\n"
        f"前50行数据:\n{sample}"
    )


class GenerateRequest(BaseModel):
    file_id: str = Field(..., description="文件 ID", alias="fileId")
    user_prompt: str = Field(..., description="用户分析需求", alias="userPrompt")
    options: Optional[dict] = Field(None, description="模型配置")
    selected_columns: Optional[list[str]] = Field(None, description="选中的列名", alias="selectedColumns")
    chart_type: Optional[str] = Field(None, description="图表类型", alias="chartType")
    chart_title: Optional[str] = Field(None, description="看板标题", alias="chartTitle")

    class Config:
        populate_by_name = True


@router.post("")
async def generate_report(request: GenerateRequest, db: Session = Depends(get_db)):
    """阶段1：分析数据并生成看板规格 JSON"""
    if not request.file_id or not request.user_prompt:
        raise HTTPException(status_code=400, detail="缺少必要参数")

    task_id = str(uuid.uuid4())

    try:
        user_config = request.options or {}
        if request.selected_columns:
            user_config["selected_columns"] = request.selected_columns
        if request.chart_type:
            user_config["chart_type"] = request.chart_type
        if request.chart_title:
            user_config["chart_title"] = request.chart_title

        create_generation_task(
            task_id=task_id,
            file_id=request.file_id,
            user_prompt=request.user_prompt,
            model_config=user_config,
        )

        # 读取文件
        await send_event(task_id, "progress", {
            "step": 1, "total": 3,
            "message": "正在读取文件数据...", "status": "processing",
        })
        update_task_status(task_id, "processing", 1, "正在读取文件数据...")

        file_dir = "uploads"
        matches = glob.glob(os.path.join(file_dir, f"{request.file_id}.*"))
        if not matches:
            raise HTTPException(status_code=404, detail="文件不存在")
        file_path = matches[0]

        file_data = _build_file_data(file_path)
        file_name = os.path.basename(file_path)

        # 调用 AI 生成看板规格
        await send_event(task_id, "progress", {
            "step": 2, "total": 3,
            "message": "正在分析数据并生成看板...", "status": "processing",
        })
        update_task_status(task_id, "processing", 2, "正在分析数据并生成看板...")

        selected_columns = user_config.get("selected_columns")
        chart_type = user_config.get("chart_type")
        chart_title = user_config.get("chart_title")

        dashboard_spec = await aiservice.generate_dashboard_spec(
            file_data=file_data,
            user_prompt=request.user_prompt,
            file_name=file_name,
            selected_columns=selected_columns,
            chart_type=chart_type,
            chart_title=chart_title,
        )

        update_task_status(task_id, "spec_ready", 2, "看板规格生成完成，等待用户确认",
                           extra={"dashboard_spec": dashboard_spec})

        await send_event(task_id, "progress", {
            "step": 3, "total": 3,
            "message": "看板规格生成完成", "status": "completed",
        })

        return create_camel_response({
            "task_id": task_id,
            "status": "spec_ready",
            "dashboard_spec": dashboard_spec,
        })

    except Exception as e:
        await send_event(task_id, "error", {"message": f"生成失败: {str(e)}"})
        update_task_status(task_id, "failed", 0, f"生成失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")


class ConfirmRequest(BaseModel):
    dashboard_spec: dict = Field(..., description="用户确认/编辑后的看板规格", alias="dashboardSpec")

    class Config:
        populate_by_name = True


@router.post("/{task_id}/confirm")
async def confirm_dashboard(task_id: str, request: ConfirmRequest, db: Session = Depends(get_db)):
    """阶段2：用户确认看板规格，保存到历史记录"""
    try:
        task = get_task_result_data(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")

        # 查找文件名
        file_dir = "uploads"
        file_id = task['file_id']
        matches = glob.glob(os.path.join(file_dir, f"{file_id}.*"))
        file_name = os.path.basename(matches[0]) if matches else "unknown"

        # 保存历史记录
        try:
            create_history(
                db=db,
                file_id=task["file_id"],
                file_name=file_name,
                user_prompt=task["user_prompt"],
                generated_prompt="",
                image_url="",
                dashboard_spec=request.dashboard_spec,
            )
        except Exception as e:
            print(f"保存历史记录失败: {e}")

        update_task_status(task_id, "completed", 3, "生成完成",
                           extra={"dashboard_spec": request.dashboard_spec})
        cleanup_task(task_id)

        return create_camel_response({
            "task_id": task_id,
            "status": "completed",
            "dashboard_spec": request.dashboard_spec,
        })

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"确认失败: {str(e)}")
