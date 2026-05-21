"""文件上传 API"""
import os
import uuid
import glob
import httpx
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
import pandas as pd
import numpy as np

from app.config import get_settings
from app.utils.file_utils import allowed_file, save_uploaded_file
from app.utils.common import create_camel_response


router = APIRouter(prefix="/upload", tags=["upload"])
settings = get_settings()


def _load_dataframe(file_path: str) -> pd.DataFrame:
    """从文件路径加载 DataFrame（支持 .xlsx / .xls / .csv）"""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.csv':
        return pd.read_csv(file_path)
    else:
        return pd.read_excel(file_path)


@router.get("/{file_id}/preview")
async def preview_file(file_id: str, rows: int = Query(50, ge=1, le=200)):
    """预览上传文件的数据内容（前 N 行 + 列信息 + 统计摘要）"""
    file_dir = "uploads"
    matches = glob.glob(os.path.join(file_dir, f"{file_id}.*"))
    if not matches:
        raise HTTPException(status_code=404, detail="文件不存在")
    file_path = matches[0]

    try:
        df = _load_dataframe(file_path)
        total_rows = len(df)
        total_cols = len(df.columns)

        # 列信息
        columns = []
        for col in df.columns:
            col_data = df[col]
            col_info = {
                "name": str(col),
                "dtype": "numeric" if pd.api.types.is_numeric_dtype(col_data) else
                         "datetime" if pd.api.types.is_datetime64_any_dtype(col_data) else
                         "text",
                "nullCount": int(col_data.isna().sum()),
            }
            # 数值列补充统计
            if col_info["dtype"] == "numeric":
                col_data_clean = col_data.dropna()
                if len(col_data_clean) > 0:
                    col_info["stats"] = {
                        "min": float(col_data_clean.min()) if np.issubdtype(col_data_clean.dtype, np.number) else None,
                        "max": float(col_data_clean.max()) if np.issubdtype(col_data_clean.dtype, np.number) else None,
                        "mean": round(float(col_data_clean.mean()), 2) if np.issubdtype(col_data_clean.dtype, np.number) else None,
                        "median": round(float(col_data_clean.median()), 2) if np.issubdtype(col_data_clean.dtype, np.number) else None,
                    }
            elif col_info["dtype"] == "text":
                col_info["uniqueValues"] = int(col_data.nunique())
            columns.append(col_info)

        # 取前 N 行数据（转为列表，处理 NaN）
        preview_rows = []
        for _, row in df.head(rows).iterrows():
            preview_rows.append([
                None if pd.isna(v) else v
                for v in row.tolist()
            ])

        return create_camel_response({
            "columns": columns,
            "rows": preview_rows,
            "totalRows": total_rows,
            "totalCols": total_cols,
            "columnNames": [c["name"] for c in columns],
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"预览失败: {str(e)}")


@router.post("")
async def upload_file(file: UploadFile = File(...)):
    """上传 Excel 文件"""
    if not file:
        raise HTTPException(status_code=400, detail="没有上传文件")
    
    if not allowed_file(file.filename, settings.ALLOWED_EXTENSIONS):
        raise HTTPException(status_code=400, detail="不支持的文件格式")
    
    try:
        file_id = str(uuid.uuid4())
        file_info = await save_uploaded_file(file, file_id)
        
        # 解析 Excel 文件
        file_path = file_info["path"]
        sheets_data = {}
        
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file_path)
            sheets_data["Sheet1"] = {
                "headers": df.columns.tolist(),
                "row_count": len(df),
                "column_count": len(df.columns)
            }
        else:
            excel_file = pd.ExcelFile(file_path)
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                sheets_data[sheet_name] = {
                    "headers": df.columns.tolist(),
                    "row_count": len(df),
                    "column_count": len(df.columns)
                }
        
        total_rows = sum(s["row_count"] for s in sheets_data.values())
        total_cols = max(s["column_count"] for s in sheets_data.values())
        
        return create_camel_response({
            "file_id": file_id,
            "file_name": file.filename,
            "file_size": file_info["size"],
            "sheets": [
                {
                    "name": name,
                    "row_count": data["row_count"],
                    "column_count": data["column_count"]
                }
                for name, data in sheets_data.items()
            ],
            "metadata": {
                "total_rows": total_rows,
                "total_cols": total_cols
            }
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件处理失败: {str(e)}")


@router.get("/{file_id}/suggest")
async def suggest_analysis(file_id: str):
    """上传数据后自动生成建议的分析提示词"""
    file_dir = "uploads"
    matches = glob.glob(os.path.join(file_dir, f"{file_id}.*"))
    if not matches:
        raise HTTPException(status_code=404, detail="文件不存在")
    file_path = matches[0]

    try:
        df = _load_dataframe(file_path)
        total_rows = len(df)
        total_cols = len(df.columns)
        columns = list(df.columns)

        # 构建列信息摘要
        col_summaries = []
        for col in columns:
            col_data = df[col]
            dtype = "numeric" if pd.api.types.is_numeric_dtype(col_data) else \
                    "datetime" if pd.api.types.is_datetime64_any_dtype(col_data) else "text"
            info = f"  - {col} ({dtype})"
            if dtype == "numeric":
                clean = col_data.dropna()
                if len(clean) > 0:
                    info += f" [min={clean.min():.2f}, max={clean.max():.2f}, mean={clean.mean():.2f}]"
            elif dtype == "text":
                info += f" [unique={col_data.nunique()}]"
            col_summaries.append(info)

        summary = f"总行数: {total_rows}, 总列数: {total_cols}\n列信息:\n" + "\n".join(col_summaries)

        # 调用 AI 生成建议提示词
        url = f"{settings.SENSENOVA_API_BASE}/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.SENSENOVA_API_KEY}",
            "Content-Type": "application/json",
        }

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

        user_prompt = f"以下是用户上传的数据摘要，请根据它生成一段建议分析提示词：\n\n{summary}"

        data = {
            "model": settings.SENSENOVA_PROMPT_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.7,
            "max_tokens": 500,
        }

        suggestion = ""
        try:
            async with httpx.AsyncClient(timeout=30.0, mounts={"all://": httpx.AsyncHTTPTransport()}) as client:
                response = await client.post(url, headers=headers, json=data)
                response.raise_for_status()
                result = response.json()

            print(f"原始 API 响应: {result}")  # 调试日志
            if "choices" in result and len(result["choices"]) > 0:
                choice = result["choices"][0]
                # 安全地提取 message.content（用 .get 避免 KeyError）
                msg = choice.get("message") or {}
                suggestion = (msg.get("content") or "").strip()
                if not suggestion:
                    suggestion = (choice.get("text") or "").strip()
                if not suggestion:
                    print(f"无法从 choice 提取内容: keys={list(choice.keys())}")
        except Exception as ai_err:
            print(f"AI 建议提示词生成失败: {ai_err}")
            import traceback
            traceback.print_exc()
            # 降级：根据数据列信息生成基础建议
            numeric_cols = [c for c in col_summaries if "(numeric)" in c]
            text_cols = [c for c in col_summaries if "(text)" in c]
            parts = ["建议分析："]
            if numeric_cols and text_cols:
                parts.append(f"数据包含{len(text_cols)}个分类列和{len(numeric_cols)}个数值列，")
                parts.append("建议使用柱状图展示不同分类的数值对比，")
                parts.append("使用折线图展示数值趋势变化。")
            elif numeric_cols:
                parts.append(f"数据包含{len(numeric_cols)}个数值列，建议使用折线图或柱状图展示数据分布。")
            elif text_cols:
                parts.append(f"数据包含{len(text_cols)}个文本列，建议分析各分类的分布情况。")
            else:
                parts.append("数据已就绪，请输入你的分析需求。")
            suggestion = "".join(parts)

        return create_camel_response({
            "suggestion": suggestion,
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成建议失败: {str(e)}")
