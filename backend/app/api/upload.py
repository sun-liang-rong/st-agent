"""文件上传 API"""
import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
import pandas as pd

from app.config import get_settings
from app.utils.file_utils import allowed_file, save_uploaded_file
from app.utils.common import create_camel_response


router = APIRouter(prefix="/upload", tags=["upload"])
settings = get_settings()


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
