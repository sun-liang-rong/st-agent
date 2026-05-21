# 数据看板生成流程重设计 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将图表生成从"AI 画图"改为"AI 生成 ECharts 配置 + 前端精确渲染"，确保数据准确性。

**Architecture:** 后端文本模型分析数据并输出 ECharts 看板 JSON，前端用 vue-echarts 渲染。去掉图像生成模型，阶段2 从调 AI 生图变为前端本地渲染。

**Tech Stack:** Python FastAPI, ECharts 5, vue-echarts 7, Vue 3, TypeScript

---

## 文件结构总览

### 后端修改
- `backend/app/services/ai_service.py` — 重写：新 prompt + `generate_dashboard_spec()`，删除图像方法
- `backend/app/api/generate.py` — 重写：新响应格式 + `/confirm` 端点
- `backend/app/api/upload.py` — 改造：`suggest` prompt 更新
- `backend/app/services/task_service.py` — 改造：存储 `dashboard_spec`
- `backend/app/models/report_history.py` — 改造：添加 `dashboard_spec` 列
- `backend/app/services/history_service.py` — 改造：保存/返回 `dashboard_spec`
- `backend/app/api/history.py` — 改造：返回 `dashboard_spec`
- `backend/app/config.py` — 清理：删除图像模型配置
- `backend/app/main.py` — 清理：删除 `generated/` 挂载

### 前端修改
- `frontend/package.json` — 新增 echarts, vue-echarts
- `frontend/src/types/index.ts` — 新增 DashboardSpec 类型，更新 Message
- `frontend/src/components/ChartCard.vue` — 新增
- `frontend/src/components/DashboardRenderer.vue` — 新增
- `frontend/src/services/api.ts` — 改造：新端点
- `frontend/src/pages/Home.vue` — 改造：新阶段2流程
- `frontend/src/pages/History.vue` — 改造：渲染看板
- `frontend/src/stores/app.ts` — 清理：删除 defaultImageModel

---

## Task 1: 后端 — 重写 ai_service.py

**Files:**
- Modify: `backend/app/services/ai_service.py`

- [ ] **Step 1: 重写 AIService 类**

替换 `backend/app/services/ai_service.py` 全部内容：

```python
"""AI 服务模块"""
import httpx
import json
from typing import Optional
from app.config import get_settings

settings = get_settings()

VALID_CHART_TYPES = {"line", "bar", "pie", "scatter", "radar", "funnel", "kline", "heatmap", "treemap"}
VALID_SIZES = {"full", "half", "third"}


def validate_dashboard_spec(spec: dict) -> tuple[bool, str]:
    """校验看板规格 JSON 格式，返回 (是否合法, 错误信息)"""
    if not isinstance(spec, dict):
        return False, "输出不是 JSON 对象"

    if "title" not in spec or not isinstance(spec["title"], str):
        return False, "缺少 title 字段或类型错误"

    if "charts" not in spec or not isinstance(spec["charts"], list):
        return False, "缺少 charts 字段或不是数组"

    if len(spec["charts"]) == 0:
        return False, "charts 数组为空"

    for i, chart in enumerate(spec["charts"]):
        prefix = f"charts[{i}]"
        if not isinstance(chart, dict):
            return False, f"{prefix} 不是对象"

        for field in ("id", "title", "type", "option"):
            if field not in chart:
                return False, f"{prefix} 缺少 {field} 字段"

        if chart["type"] not in VALID_CHART_TYPES:
            return False, f"{prefix}.type '{chart['type']}' 不是合法的图表类型，允许: {VALID_CHART_TYPES}"

        if "size" in chart and chart["size"] not in VALID_SIZES:
            return False, f"{prefix}.size '{chart['size']}' 不合法，允许: {VALID_SIZES}"

        if not isinstance(chart["option"], dict):
            return False, f"{prefix}.option 不是对象"

        if "series" not in chart["option"]:
            return False, f"{prefix}.option 缺少 series 字段"

    return True, ""


class AIService:
    """AI 服务类"""

    def __init__(self):
        self.api_key = settings.SENSENOVA_API_KEY
        self.api_base = settings.SENSENOVA_API_BASE
        self.prompt_model = settings.SENSENOVA_PROMPT_MODEL

    async def generate_dashboard_spec(
        self,
        file_data: str,
        user_prompt: str,
        file_name: str = "data.xlsx",
        selected_columns: list[str] | None = None,
        chart_type: str | None = None,
        chart_title: str | None = None,
    ) -> dict:
        """
        分析数据并生成看板规格 JSON
        返回合法的 DashboardSpec dict
        """
        # 构建用户偏好描述
        user_prefs = []
        if selected_columns:
            user_prefs.append(f"重点关注以下列: {', '.join(selected_columns)}")
        if chart_type:
            user_prefs.append(f"用户希望的图表类型: {chart_type}")
        if chart_title:
            user_prefs.append(f"用户指定的看板标题: {chart_title}")
        user_prefs_text = "\n".join(user_prefs) if user_prefs else ""

        system_prompt = f"""你是一个数据可视化专家。用户会提供 Excel 数据，你需要分析数据并生成一个数据看板的 ECharts 配置。

{'## 用户偏好\n' + user_prefs_text + '\n' if user_prefs_text else ''}
## 输出要求

你必须输出一个合法的 JSON 对象，格式如下：

```json
{{
  "title": "看板标题",
  "description": "简短描述",
  "charts": [
    {{
      "id": "chart-1",
      "title": "图表标题",
      "type": "line",
      "size": "full",
      "option": {{
        // 标准 ECharts option
        "xAxis": {{ "type": "category", "data": [...] }},
        "yAxis": {{ "type": "value" }},
        "series": [{{ "data": [...], "type": "line" }}]
      }}
    }}
  ]
}}
```

## 规则

1. 输出必须是合法 JSON，不要包含任何其他文字、代码块标记或解释
2. 每个 chart 的 option 必须是标准 ECharts option，可直接用 echarts.setOption(option) 渲染
3. 数据值必须来自原始数据，禁止编造数字
4. 中文分类名保留原文（如"华东"、"产品A"）
5. charts 数组至少包含 2 个图表，最多 6 个
6. type 合法值: line, bar, pie, scatter, radar, funnel, kline, heatmap, treemap
7. size 合法值: full（独占一行）, half（占半行）, third（占1/3行）
8. 趋势类图表用 full，占比类用 half，统计卡片用 third
9. 颜色使用 ECharts 默认主题色或标准 CSS 颜色名
10. 如果用户指定了标题，必须使用用户指定的标题

## 图表类型选择指南

- 时间序列/趋势 → line (full)
- 分类对比 → bar (full 或 half)
- 占比分布 → pie (half)
- 两变量关系 → scatter (half)
- 多维对比 → radar (half)
- 漏斗分析 → funnel (half)
- KPI 指标 → 使用 bar/line 配合特殊样式 (third)"""

        data = {
            "model": self.prompt_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"文件名: {file_name}\n\n用户需求: {user_prompt}\n\n数据:\n{file_data}"},
            ],
            "temperature": 0.3,
            "max_tokens": 4000,
        }

        # 最多重试 2 次
        last_error = ""
        for attempt in range(2):
            async with httpx.AsyncClient(timeout=120.0, proxy=None) as client:
                response = await client.post(
                    f"{self.api_base}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                    json=data,
                )
                response.raise_for_status()
                result = response.json()

            if "choices" not in result or len(result["choices"]) == 0:
                raise Exception(f"API 返回格式错误: {result}")

            content = result["choices"][0]["message"]["content"].strip()

            # 尝试提取 JSON（处理 AI 可能包裹 ```json ``` 的情况）
            if content.startswith("```"):
                lines = content.split("\n")
                json_lines = []
                in_block = False
                for line in lines:
                    if line.strip().startswith("```") and not in_block:
                        in_block = True
                        continue
                    elif line.strip() == "```" and in_block:
                        break
                    elif in_block:
                        json_lines.append(line)
                content = "\n".join(json_lines)

            try:
                spec = json.loads(content)
            except json.JSONDecodeError as e:
                last_error = f"AI 输出不是合法 JSON: {e}"
                # 重试时强调输出格式
                data["messages"].append({"role": "assistant", "content": content})
                data["messages"].append({"role": "user", "content": "你的输出不是合法 JSON。请只输出 JSON 对象，不要包含其他文字。重新生成。"})
                continue

            valid, err = validate_dashboard_spec(spec)
            if not valid:
                last_error = f"看板规格校验失败: {err}"
                data["messages"].append({"role": "assistant", "content": content})
                data["messages"].append({"role": "user", "content": f"格式错误: {err}。请修正后重新输出合法的 JSON。"})
                continue

            return spec

        raise Exception(f"AI 生成看板规格失败（已重试2次）: {last_error}")


aiservice = AIService()
```

- [ ] **Step 2: 验证语法**

Run: `cd E:/my-project/st-agent/backend && python -c "from app.services.ai_service import aiservice, validate_dashboard_spec; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add backend/app/services/ai_service.py
git commit -m "refactor: rewrite ai_service to generate ECharts dashboard spec instead of image prompt"
```

---

## Task 2: 后端 — 重写 generate.py

**Files:**
- Modify: `backend/app/api/generate.py`

- [ ] **Step 1: 重写 generate.py**

替换 `backend/app/api/generate.py` 全部内容：

```python
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
                generated_prompt="",  # 不再使用
                image_url="",  # 不再使用
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
```

- [ ] **Step 2: 验证语法**

Run: `cd E:/my-project/st-agent/backend && python -c "from app.api.generate import router; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add backend/app/api/generate.py
git commit -m "refactor: rewrite generate API for ECharts dashboard spec flow"
```

---

## Task 3: 后端 — 更新 task_service.py

**Files:**
- Modify: `backend/app/services/task_service.py`

- [ ] **Step 1: 更新 get_task_result**

在 `get_task_result` 函数中，将 `image_url` 替换为 `dashboard_spec`：

```python
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
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/services/task_service.py
git commit -m "refactor: update task_service to use dashboard_spec"
```

---

## Task 4: 后端 — 更新 history 模型 + 服务 + API

**Files:**
- Modify: `backend/app/models/report_history.py`
- Modify: `backend/app/services/history_service.py`
- Modify: `backend/app/api/history.py`

- [ ] **Step 1: 更新 report_history 模型**

在 `backend/app/models/report_history.py` 中添加 `dashboard_spec` 列：

```python
"""报表历史记录模型"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.models.database import Base


class ReportHistory(Base):
    """报表生成历史记录表"""
    __tablename__ = "report_histories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    file_id = Column(String(64), nullable=False, comment="上传文件 ID")
    file_name = Column(String(255), nullable=False, comment="原始文件名")
    user_prompt = Column(Text, nullable=False, comment="用户分析需求")
    generated_prompt = Column(Text, nullable=True, comment="AI 生成的提示词（已废弃）")
    image_url = Column(String(1024), nullable=True, comment="生成的图片 URL（已废弃）")
    dashboard_spec = Column(Text, nullable=True, comment="看板规格 JSON")
    status = Column(String(20), nullable=False, default="completed", comment="状态: completed/failed")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<ReportHistory {self.id} ({self.file_name})>"
```

- [ ] **Step 2: 更新 history_service.py**

更新 `create_history` 函数签名，添加 `dashboard_spec` 参数：

```python
"""历史记录服务模块"""
import json
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.report_history import ReportHistory


def create_history(
    db: Session,
    file_id: str,
    file_name: str,
    user_prompt: str,
    generated_prompt: str = "",
    image_url: str = "",
    dashboard_spec: Optional[dict] = None,
    user_id: Optional[int] = None,
    status: str = "completed",
) -> ReportHistory:
    """创建一条历史记录"""
    record = ReportHistory(
        user_id=user_id,
        file_id=file_id,
        file_name=file_name,
        user_prompt=user_prompt,
        generated_prompt=generated_prompt,
        image_url=image_url,
        dashboard_spec=json.dumps(dashboard_spec, ensure_ascii=False) if dashboard_spec else None,
        status=status,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_history_list(db: Session, user_id: Optional[int] = None) -> List[ReportHistory]:
    """获取历史记录列表（按创建时间倒序）"""
    query = db.query(ReportHistory)
    if user_id is not None:
        query = query.filter(ReportHistory.user_id == user_id)
    return query.order_by(ReportHistory.created_at.desc()).all()


def get_history_detail(db: Session, history_id: int) -> Optional[ReportHistory]:
    """获取单条历史记录详情"""
    return db.query(ReportHistory).filter(ReportHistory.id == history_id).first()


def delete_history(db: Session, history_id: int, user_id: Optional[int] = None) -> bool:
    """删除历史记录，只允许删除自己的"""
    query = db.query(ReportHistory).filter(ReportHistory.id == history_id)
    if user_id is not None:
        query = query.filter(ReportHistory.user_id == user_id)
    record = query.first()
    if not record:
        return False
    db.delete(record)
    db.commit()
    return True
```

- [ ] **Step 3: 更新 history.py API**

在 `backend/app/api/history.py` 的响应中添加 `dashboard_spec` 字段：

```python
"""历史记录 API"""
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models import get_db
from app.services.history_service import (
    get_history_list,
    get_history_detail,
    delete_history,
)
from app.utils.common import create_camel_response


router = APIRouter(prefix="/history", tags=["history"])


@router.get("")
async def get_history(db: Session = Depends(get_db)):
    """获取历史记录列表（按时间倒序）"""
    records = get_history_list(db)
    data = []
    for r in records:
        dashboard_spec = None
        if r.dashboard_spec:
            try:
                dashboard_spec = json.loads(r.dashboard_spec)
            except json.JSONDecodeError:
                pass
        data.append({
            "id": str(r.id),
            "file_id": r.file_id,
            "file_name": r.file_name,
            "user_prompt": r.user_prompt,
            "dashboard_spec": dashboard_spec,
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else "",
            "updated_at": r.updated_at.isoformat() if r.updated_at else "",
        })
    return create_camel_response({"data": data})


@router.get("/{history_id}")
async def get_history_detail_endpoint(history_id: int, db: Session = Depends(get_db)):
    """获取单条历史记录详情"""
    record = get_history_detail(db, history_id)
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    dashboard_spec = None
    if record.dashboard_spec:
        try:
            dashboard_spec = json.loads(record.dashboard_spec)
        except json.JSONDecodeError:
            pass
    return create_camel_response({
        "id": str(record.id),
        "file_id": record.file_id,
        "file_name": record.file_name,
        "user_prompt": record.user_prompt,
        "dashboard_spec": dashboard_spec,
        "status": record.status,
        "created_at": record.created_at.isoformat() if record.created_at else "",
        "updated_at": record.updated_at.isoformat() if record.updated_at else "",
    })


@router.delete("/{history_id}")
async def delete_history_endpoint(history_id: int, db: Session = Depends(get_db)):
    """删除历史记录"""
    success = delete_history(db, history_id)
    if not success:
        raise HTTPException(status_code=404, detail="记录不存在")
    return {"message": "删除成功"}
```

- [ ] **Step 4: 验证语法**

Run: `cd E:/my-project/st-agent/backend && python -c "from app.api.history import router; from app.services.history_service import create_history; print('OK')"`
Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git add backend/app/models/report_history.py backend/app/services/history_service.py backend/app/api/history.py
git commit -m "feat: add dashboard_spec to history model and API"
```

---

## Task 5: 后端 — 更新 upload.py suggest 接口

**Files:**
- Modify: `backend/app/api/upload.py` (suggest_analysis 函数)

- [ ] **Step 1: 更新 suggest 的 system prompt**

在 `backend/app/api/upload.py` 中，找到 `suggest_analysis` 函数，替换 `system_prompt` 变量：

```python
        system_prompt = """你是一个数据可视化专家助手。你的任务是：根据用户上传的 Excel 数据摘要，生成一段简短的建议分析方向。

要求：
1. 用中文，一段话即可，不要长篇大论
2. 指出数据中值得关注的列和可能的分析方向
3. 推荐可以生成的图表类型（如：柱状图对比、折线图趋势、饼图占比等）
4. 语气自然，像在给用户提建议
5. 长度在 80-200 字之间
6. 以"建议分析："开头

例如：
"建议分析：数据包含'地区'（分类）和'销售额'（数值）两列，建议生成各地区销售额对比的柱状图，也可以用饼图展示各地区销售占比。如果有日期列，还可以生成月度销售趋势折线图。"
"""
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/api/upload.py
git commit -m "refactor: update suggest prompt for dashboard direction"
```

---

## Task 6: 后端 — 清理 config.py 和 main.py

**Files:**
- Modify: `backend/app/config.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: 清理 config.py**

在 `backend/app/config.py` 中，删除 `SENSENOVA_IMAGE_MODEL` 行：

```python
    SENSENOVA_API_KEY: str = "sk-8JEVTH1zNypwQqa9z9fghTfJ2coqpceD"
    SENSENOVA_PROMPT_MODEL: str = "sensenova-6.7-flash-lite"
    # 删除这行: SENSENOVA_IMAGE_MODEL: str = "sensenova-u1-fast"
    SENSENOVA_API_BASE: str = "https://token.sensenova.cn/v1"
```

- [ ] **Step 2: 清理 main.py**

在 `backend/app/main.py` 中，删除 `generated/` 静态文件挂载：

```python
# 删除这行:
# app.mount("/generated", StaticFiles(directory="generated"), name="generated")
```

同时删除不再需要的 `StaticFiles` import（如果只用于此）：

```python
# 将
from fastapi.staticfiles import StaticFiles
# 改为（如果其他地方不用 StaticFiles 则删除此行）
```

- [ ] **Step 3: 验证**

Run: `cd E:/my-project/st-agent/backend && python -c "from app.main import app; print('OK')"`
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add backend/app/config.py backend/app/main.py
git commit -m "cleanup: remove image model config and generated/ static mount"
```

---

## Task 7: 前端 — 安装 ECharts 依赖

**Files:**
- Modify: `frontend/package.json`

- [ ] **Step 1: 安装依赖**

Run: `cd E:/my-project/st-agent/frontend && npm install echarts vue-echarts`

Expected: `added 2 packages` (or similar)

- [ ] **Step 2: Commit**

```bash
git add frontend/package.json frontend/package-lock.json
git commit -m "feat: add echarts and vue-echarts dependencies"
```

---

## Task 8: 前端 — 更新类型定义

**Files:**
- Modify: `frontend/src/types/index.ts`

- [ ] **Step 1: 添加新类型，更新现有类型**

在 `frontend/src/types/index.ts` 中进行以下修改：

1. 在文件顶部添加 `DashboardChart` 和 `DashboardSpec` 类型
2. 在 `Message` 接口中添加 `dashboardSpec` 字段
3. 更新 `GenerateResponse` 添加 `dashboardSpec`
4. 删除 `GenerateImageResponse`（不再使用）
5. 更新 `ChatHistory` 移除 `imageUrl`
6. 更新 `UserSettings` 移除 `defaultImageModel`

```typescript
// ── 看板相关类型 ──

export interface DashboardChart {
  id: string;
  title: string;
  type: 'line' | 'bar' | 'pie' | 'scatter' | 'radar' | 'funnel' | 'kline' | 'heatmap' | 'treemap';
  size: 'full' | 'half' | 'third';
  option: Record<string, any>;
}

export interface DashboardSpec {
  title: string;
  description?: string;
  charts: DashboardChart[];
}

// 消息类型（更新）
export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: number;
  attachments?: FileAttachment[];
  imageUrl?: string;              // 保留兼容
  dashboardSpec?: DashboardSpec;  // 新增：看板规格
  progress?: ProgressInfo;
  promptForReview?: string;
  phase?: 'prompt' | 'complete';
}

// 生成响应（更新）
export interface GenerateResponse {
  taskId: string;
  status: 'pending' | 'processing' | 'spec_ready' | 'completed' | 'failed';
  dashboardSpec?: DashboardSpec;
  message?: string;
}

// 删除 GenerateImageResponse（整个接口删除）

// 对话历史（更新）
export interface ChatHistory {
  id: string;
  title: string;
  userPrompt: string;
  generatedPrompt: string;
  dashboardSpec?: DashboardSpec;
  fileName: string;
  createdAt: string;
  updatedAt: string;
}

// 用户设置（更新）
export interface UserSettings {
  theme: 'light' | 'dark';
  fontSize: 'small' | 'medium' | 'large';
  codeFont: 'mono' | 'system';
  messageDensity: 'comfortable' | 'compact';
  defaultPromptModel: string;
  // 删除 defaultImageModel
  apiKeys: {
    shangtang?: string;
  };
}
```

- [ ] **Step 2: 验证类型无报错**

Run: `cd E:/my-project/st-agent/frontend && npx vue-tsc --noEmit 2>&1 | head -20`
Expected: 可能有一些已有的类型错误，但不应有新增的 `DashboardSpec` 相关错误

- [ ] **Step 3: Commit**

```bash
git add frontend/src/types/index.ts
git commit -m "feat: add DashboardSpec types, update Message and GenerateResponse"
```

---

## Task 9: 前端 — 创建 ChartCard.vue

**Files:**
- Create: `frontend/src/components/ChartCard.vue`

- [ ] **Step 1: 创建 ChartCard 组件**

```vue
<template>
  <div class="bg-white dark:bg-slate-800 rounded-xl border border-gray-100 dark:border-slate-700/50 shadow-sm overflow-hidden transition-all hover:shadow-md"
       :class="sizeClass">
    <div class="px-4 pt-4 pb-2">
      <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-200">{{ title }}</h3>
    </div>
    <div class="px-2 pb-2">
      <div v-if="error" class="flex flex-col items-center justify-center h-48 text-center px-4">
        <svg class="w-8 h-8 text-red-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"/>
        </svg>
        <p class="text-xs text-red-500 dark:text-red-400">{{ error }}</p>
      </div>
      <v-chart v-else ref="chartRef" :option="option" :autoresize="true" style="height: 280px; width: 100%;" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, LineChart, PieChart, ScatterChart, RadarChart, FunnelChart, HeatmapChart, TreemapChart } from 'echarts/charts'
import {
  TitleComponent, TooltipComponent, LegendComponent, GridComponent,
  DatasetComponent, TransformComponent, ToolboxComponent, DataZoomComponent,
  VisualMapComponent,
} from 'echarts/components'

use([
  CanvasRenderer,
  BarChart, LineChart, PieChart, ScatterChart, RadarChart, FunnelChart, HeatmapChart, TreemapChart,
  TitleComponent, TooltipComponent, LegendComponent, GridComponent,
  DatasetComponent, TransformComponent, ToolboxComponent, DataZoomComponent,
  VisualMapComponent,
])

const props = defineProps<{
  title: string
  option: Record<string, any>
  size?: 'full' | 'half' | 'third'
}>()

const chartRef = ref<InstanceType<typeof VChart> | null>(null)
const error = ref<string>('')

const sizeClass = computed(() => {
  switch (props.size) {
    case 'full': return 'col-span-1 md:col-span-2'
    case 'third': return 'col-span-1'
    case 'half':
    default: return 'col-span-1'
  }
})

// 校验 option 合法性
function validateOption(opt: Record<string, any>): string {
  if (!opt || typeof opt !== 'object') return '图表配置不是对象'
  if (!opt.series) return '缺少 series 字段'
  return ''
}

onMounted(() => {
  error.value = validateOption(props.option)
})

watch(() => props.option, (newOpt) => {
  error.value = validateOption(newOpt)
}, { deep: true })
</script>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/ChartCard.vue
git commit -m "feat: create ChartCard component with ECharts rendering"
```

---

## Task 10: 前端 — 创建 DashboardRenderer.vue

**Files:**
- Create: `frontend/src/components/DashboardRenderer.vue`

- [ ] **Step 1: 创建 DashboardRenderer 组件**

```vue
<template>
  <div class="space-y-4">
    <!-- 看板标题 -->
    <div v-if="spec.title" class="mb-2">
      <h2 class="text-lg font-bold text-gray-800 dark:text-white">{{ spec.title }}</h2>
      <p v-if="spec.description" class="text-sm text-gray-500 dark:text-gray-400 mt-1">{{ spec.description }}</p>
    </div>

    <!-- 图表网格 -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <ChartCard
        v-for="chart in spec.charts"
        :key="chart.id"
        :title="chart.title"
        :option="chart.option"
        :size="chart.size"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { DashboardSpec } from '@/types'
import ChartCard from './ChartCard.vue'

defineProps<{
  spec: DashboardSpec
}>()
</script>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/DashboardRenderer.vue
git commit -m "feat: create DashboardRenderer component"
```

---

## Task 11: 前端 — 更新 api.ts

**Files:**
- Modify: `frontend/src/services/api.ts`

- [ ] **Step 1: 更新 api.ts**

1. 更新 import 类型，移除 `GenerateImageResponse`，添加 `DashboardSpec`
2. 删除 `generateImage` 方法
3. 添加 `confirmDashboard` 方法
4. 更新 `generateReport` 返回类型

```typescript
import axios from 'axios'
import type { UploadResponse, GenerateRequest, GenerateResponse, TaskStatusResponse, PreviewResponse, SuggestResponse, DashboardSpec } from '@/types'

// ... axios 实例和拦截器保持不变 ...

export const apiService = {
  // 上传文件（不变）
  uploadFile(file: File): Promise<UploadResponse> {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  // 生成报表（不变）
  generateReport(request: GenerateRequest): Promise<GenerateResponse> {
    return api.post('/generate', request)
  },

  // 预览文件数据（不变）
  getFilePreview(fileId: string, rows: number = 50): Promise<PreviewResponse> {
    return api.get(`/upload/${fileId}/preview`, { params: { rows } })
  },

  // 获取 AI 建议（不变）
  suggestPrompt(fileId: string): Promise<SuggestResponse> {
    return api.get(`/upload/${fileId}/suggest`)
  },

  // 确认看板（新增，替代 generateImage）
  confirmDashboard(taskId: string, dashboardSpec: DashboardSpec): Promise<any> {
    return api.post(`/generate/${taskId}/confirm`, { dashboardSpec })
  },

  // 删除 generateImage（不再需要）

  // 查询任务状态（不变）
  getTaskStatus(taskId: string): Promise<TaskStatusResponse> {
    return api.get(`/task/${taskId}`)
  },

  // 获取任务结果（不变）
  getTaskResult(taskId: string): Promise<TaskStatusResponse> {
    return api.get(`/task/${taskId}/result`)
  },

  // AI 聊天（不变）
  chat(message: string): Promise<{ reply: string }> {
    return api.post('/chat', { message })
  },

  getChatHistory() { return api.get('/chat/history') },
  getChatHistoryDetail(id: string) { return api.get(`/chat/history/${id}`) },
  deleteChatHistory(id: string) { return api.delete(`/chat/history/${id}`) },

  // 历史记录（不变）
  getHistory() { return api.get('/history') },
  getHistoryDetail(id: string) { return api.get(`/history/${id}`) },
  deleteHistory(id: string) { return api.delete(`/history/${id}`) },

  // 收藏（不变）
  collectReport(reportId: string) { return api.post(`/collect/${reportId}`) },
  uncollectReport(reportId: string) { return api.delete(`/collect/${reportId}`) },
  getCollections() { return api.get('/collections') },

  // 设置（不变）
  getSettings() { return api.get('/settings') },
  updateSettings(settings: any) { return api.put('/settings', settings) }
}

export default api
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/services/api.ts
git commit -m "refactor: replace generateImage with confirmDashboard in api service"
```

---

## Task 12: 前端 — 重写 Home.vue 阶段2 流程

**Files:**
- Modify: `frontend/src/pages/Home.vue`

- [ ] **Step 1: 更新 import**

在 `<script setup>` 中添加 DashboardRenderer import，移除不再需要的导入：

```typescript
import DashboardRenderer from '@/components/DashboardRenderer.vue'
import type { DashboardSpec } from '@/types'
```

- [ ] **Step 2: 添加 dashboardSpec 编辑状态**

在 `Home.vue` 的 script setup 中，添加编辑状态变量：

```typescript
// 在现有状态变量附近添加
const editingSpec = ref<DashboardSpec | null>(null)
```

- [ ] **Step 3: 修改 generatePhase1 函数**

将 `generatePhase1` 中展示 prompt 确认的逻辑改为展示看板规格确认：

```typescript
async function generatePhase1(
  fileId: string,
  userPrompt: string,
  selectedColumns: string[] = [],
  chartType: string = 'bar',
  chartTitle: string = '',
) {
  appStore.setLoading(true)

  try {
    const thinkingMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: '正在分析数据...',
      timestamp: Date.now(),
      progress: { step: 0, total: 3, message: '准备中...' }
    }
    appStore.addMessage(thinkingMessage)

    const generateResponse = await apiService.generateReport({
      fileId: fileId,
      userPrompt: userPrompt,
      selectedColumns: selectedColumns.length > 0 ? selectedColumns : undefined,
      chartType: chartType,
      chartTitle: chartTitle || undefined,
    } as any)

    currentTaskId.value = generateResponse.taskId
    const dashboardSpec = generateResponse.dashboardSpec

    // 连接 SSE 获取进度
    connectSSE(generateResponse.taskId, thinkingMessage.id)

    // 展示看板预览，等待用户确认
    const idx = appStore.messages.findIndex(m => m.id === thinkingMessage.id)
    if (idx > -1 && dashboardSpec) {
      appStore.messages[idx] = {
        ...appStore.messages[idx],
        content: '',
        progress: undefined,
        phase: 'prompt',
        dashboardSpec: dashboardSpec,
      }
      editingSpec.value = dashboardSpec
    }
    appStore.setLoading(false)

  } catch (error) {
    console.error('生成失败:', error)
    const errorMessage: Message = {
      id: (Date.now() + 2).toString(),
      role: 'assistant',
      content: '生成报表时出错，请重试',
      timestamp: Date.now()
    }
    appStore.addMessage(errorMessage)
    appStore.setLoading(false)
    closeSSE()
  }
}
```

- [ ] **Step 4: 修改 confirmGenerate 函数**

将 `confirmGenerate` 改为调用 `confirmDashboard` 而非 `generateImage`：

```typescript
async function confirmGenerate(message: Message) {
  if (!editingSpec.value || !currentTaskId.value) return

  isPhase2Loading.value = true
  appStore.setLoading(true)

  try {
    // 更新消息为渲染中状态
    const idx = appStore.messages.findIndex(m => m.id === message.id)
    if (idx > -1) {
      appStore.messages[idx] = {
        ...appStore.messages[idx],
        content: '',
        phase: 'complete',
        dashboardSpec: editingSpec.value,
        progress: undefined,
      }
    }

    // 调用后端保存确认的看板规格
    await apiService.confirmDashboard(currentTaskId.value, editingSpec.value)

  } catch (error) {
    console.error('保存失败:', error)
    const idx = appStore.messages.findIndex(m => m.id === message.id)
    if (idx > -1) {
      appStore.messages[idx] = {
        ...appStore.messages[idx],
        content: '保存失败，请重试',
        progress: undefined,
      }
    }
  } finally {
    isPhase2Loading.value = false
    appStore.setLoading(false)
    closeSSE()
  }
}
```

- [ ] **Step 5: 修改模板中的消息渲染**

在 Home.vue 的 `<template>` 中，找到消息渲染部分（`v-for="message in messages"` 循环内），在 `message.imageUrl` 渲染块之后，添加看板渲染：

```html
<!-- 生成的看板 -->
<div v-if="message.dashboardSpec && message.phase === 'complete'" class="mt-4">
  <DashboardRenderer :spec="message.dashboardSpec" />
</div>
```

同时修改 prompt 确认区域（`v-if="message.phase === 'prompt'"` 部分），将 textarea 替换为看板预览 + JSON 编辑器：

```html
<!-- 看板预览确认（两阶段模式） -->
<div v-if="message.phase === 'prompt' && message.dashboardSpec" class="mt-3 space-y-3">
  <div class="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-700 rounded-lg p-3">
    <p class="text-sm font-medium text-gray-800 dark:text-gray-200">📊 看板方案已生成</p>
    <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">AI 生成了以下看板配置，你可以编辑后确认渲染</p>
  </div>

  <!-- 看板预览 -->
  <DashboardRenderer :spec="message.dashboardSpec" />

  <!-- JSON 编辑区（可折叠） -->
  <details class="bg-gray-50 dark:bg-slate-700/30 rounded-lg border border-gray-200 dark:border-slate-600">
    <summary class="px-4 py-2 text-sm font-medium text-gray-600 dark:text-gray-300 cursor-pointer hover:bg-gray-100 dark:hover:bg-slate-700/50 rounded-lg transition-colors">
      编辑 JSON 配置
    </summary>
    <div class="px-4 pb-4">
      <textarea
        :value="JSON.stringify(editingSpec, null, 2)"
        @input="onSpecEdit($event)"
        rows="12"
        class="w-full px-3 py-2 bg-white dark:bg-slate-700 border border-gray-200 dark:border-slate-600 rounded-lg text-xs text-gray-800 dark:text-white font-mono focus:outline-none focus:ring-2 focus:ring-primary-500/40 transition-all resize-y"
        placeholder="看板 JSON 配置..."
        :disabled="isPhase2Loading"
      ></textarea>
    </div>
  </details>

  <div class="flex gap-2">
    <button
      @click="confirmGenerate(message)"
      :disabled="isPhase2Loading"
      class="flex-1 py-2.5 px-4 bg-gradient-to-r from-primary-600 to-primary-500 hover:from-primary-700 hover:to-primary-600 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-xl text-sm font-medium shadow-lg shadow-primary-200 dark:shadow-primary-900/30 transition-all duration-200 flex items-center justify-center gap-2"
    >
      <svg v-if="isPhase2Loading" class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
      </svg>
      {{ isPhase2Loading ? '渲染中...' : '✅ 确认渲染看板' }}
    </button>
    <button
      @click="cancelAndRetry(message)"
      :disabled="isPhase2Loading"
      class="py-2.5 px-4 bg-gray-100 dark:bg-slate-700 text-gray-600 dark:text-gray-300 rounded-xl text-sm font-medium hover:bg-gray-200 dark:hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
    >
      🔄 重新分析
    </button>
  </div>
</div>
```

- [ ] **Step 6: 添加 JSON 编辑处理函数**

在 script setup 中添加：

```typescript
function onSpecEdit(event: Event) {
  const target = event.target as HTMLTextAreaElement
  try {
    const parsed = JSON.parse(target.value)
    editingSpec.value = parsed
    // 同时更新消息中的 dashboardSpec 以实时预览
    const msg = appStore.messages.find(m => m.phase === 'prompt' && m.dashboardSpec)
    if (msg) {
      msg.dashboardSpec = parsed
    }
  } catch {
    // JSON 不合法，不更新（保留上次合法状态）
  }
}
```

- [ ] **Step 7: 更新 cancelAndRetry 函数**

```typescript
function cancelAndRetry(message: Message) {
  const idx = appStore.messages.findIndex(m => m.id === message.id)
  if (idx > -1) {
    appStore.messages.splice(idx, 1)
  }
  editingSpec.value = null
}
```

- [ ] **Step 8: 更新 loadHistory 函数**

在 `loadHistory` 函数中，将 `imageUrl` 替换为 `dashboardSpec`：

```typescript
async function loadHistory(type: string, id: string) {
  appStore.clearMessages()
  try {
    if (type === 'chat') {
      const res: any = await apiService.getChatHistoryDetail(id)
      const d = res as any
      appStore.addMessage({ id: 'hist-user', role: 'user', content: d.userMessage || '', timestamp: Date.now() })
      appStore.addMessage({ id: 'hist-ai', role: 'assistant', content: d.aiReply || '', timestamp: Date.now() + 1 })
    } else {
      const res: any = await apiService.getHistoryDetail(id)
      const d = res as any
      appStore.addMessage({ id: 'hist-user', role: 'user', content: d.userPrompt || '', timestamp: Date.now() })
      if (d.dashboardSpec) {
        appStore.addMessage({
          id: 'hist-ai',
          role: 'assistant',
          content: '',
          dashboardSpec: d.dashboardSpec,
          phase: 'complete',
          timestamp: Date.now() + 1,
        })
      }
    }
  } catch (e) {
    console.error('加载历史记录失败:', e)
  }
}
```

同样更新 `loadHistoryItems` 函数中的 report 部分：

```typescript
// 在 loadHistoryItems 中，替换 imageUrl 相关逻辑：
if (d.dashboardSpec) {
  appStore.addMessage({
    id: `hist-report-${item.rawId}-ai`,
    role: 'assistant',
    content: '',
    dashboardSpec: d.dashboardSpec,
    phase: 'complete',
    timestamp: baseTime + 1,
  })
}
```

- [ ] **Step 9: 清理不再需要的代码**

删除以下不再使用的代码：
- `downloadImage` 函数
- `ImagePreview` 组件的 import 和使用
- `previewImageUrl` ref

- [ ] **Step 10: 验证前端编译**

Run: `cd E:/my-project/st-agent/frontend && npx vue-tsc --noEmit 2>&1 | head -20`
Expected: 无新增类型错误

- [ ] **Step 11: Commit**

```bash
git add frontend/src/pages/Home.vue
git commit -m "refactor: rewrite Home.vue phase 2 to render ECharts dashboard instead of AI image"
```

---

## Task 13: 前端 — 更新 History.vue

**Files:**
- Modify: `frontend/src/pages/History.vue`

- [ ] **Step 1: 更新历史记录展示**

在 History.vue 的模板中，历史记录卡片的 summary 部分，将 `imageUrl` 相关展示移除，改为展示是否有看板：

```html
<p class="text-sm text-gray-500 dark:text-gray-400 mt-1 line-clamp-2">
  {{ group.summary }}
</p>
```

在 script setup 中，更新 `openGroup` 函数的路由跳转（已经使用 `historyItems` 参数，无需大改）。

在 `buildGroup` 函数中，如果需要在列表中显示看板缩略信息，可以添加：

```typescript
function buildGroup(items: RawItem[]): HistoryGroup {
  const first = items[0]
  const last = items[items.length - 1]
  return {
    id: `group-${first.rawId}`,
    title: first.title,
    summary: first.summary,
    createdAt: last.createdAt,
    count: items.length,
    items,
  }
}
```

这部分改动较小，主要是确保历史记录加载后，Home.vue 能正确渲染 `dashboardSpec`。

- [ ] **Step 2: Commit**

```bash
git add frontend/src/pages/History.vue
git commit -m "refactor: update History.vue for dashboard spec flow"
```

---

## Task 14: 前端 — 更新 stores/app.ts

**Files:**
- Modify: `frontend/src/stores/app.ts`

- [ ] **Step 1: 清理 settings 中的 defaultImageModel**

在 `backend/app/stores/app.ts` 的 settings ref 中，删除 `defaultImageModel`：

```typescript
const settings = ref<UserSettings>({
  theme: 'light',
  fontSize: 'medium',
  codeFont: 'mono',
  messageDensity: 'comfortable',
  defaultPromptModel: 'shangtang-model-a',
  // 删除这行: defaultImageModel: 'shangtang-model-b',
  apiKeys: {}
})
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/stores/app.ts
git commit -m "cleanup: remove defaultImageModel from app store"
```

---

## Task 15: 端到端验证

- [ ] **Step 1: 启动后端**

Run: `cd E:/my-project/st-agent/backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
Expected: 服务启动成功，无报错

- [ ] **Step 2: 启动前端**

Run: `cd E:/my-project/st-agent/frontend && npm run dev`
Expected: Vite 启动成功

- [ ] **Step 3: 测试完整流程**

1. 打开浏览器访问前端地址
2. 上传一个 Excel 文件
3. 输入分析需求
4. 验证阶段1 返回看板 JSON 并预览
5. 点击"确认渲染看板"
6. 验证 ECharts 图表正确渲染
7. 查看历史记录，确认可以加载之前的看板

- [ ] **Step 4: 最终 Commit**

```bash
git add -A
git commit -m "feat: complete dashboard flow redesign - ECharts rendering replaces AI image generation"
```
