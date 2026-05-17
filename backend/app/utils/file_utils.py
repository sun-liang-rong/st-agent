"""文件处理工具"""
import os
from fastapi import UploadFile
from typing import Dict


def allowed_file(filename: str, allowed_extensions: str) -> bool:
    """检查文件扩展名是否允许"""
    if not filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    allowed = allowed_extensions.split(',')
    return ext in allowed


async def save_uploaded_file(file: UploadFile, file_id: str) -> Dict:
    """保存上传的文件"""
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'xlsx'
    filename = f"{file_id}.{file_ext}"
    file_path = os.path.join(upload_dir, filename)
    
    content = await file.read()
    with open(file_path, "wb") as buffer:
        buffer.write(content)
    
    return {
        "id": file_id,
        "name": file.filename,
        "path": file_path,
        "size": len(content),
        "extension": file_ext
    }
