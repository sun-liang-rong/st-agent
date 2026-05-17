"""AI 聊天 API"""
import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import get_db
from app.services.chat_history_service import save_chat, get_chat_list, get_chat_detail, delete_chat
from app.utils.common import create_camel_response


router = APIRouter(prefix="/chat", tags=["chat"])
settings = get_settings()


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="用户消息")


@router.post("")
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """与 AI 自由对话（自动保存聊天记录）"""
    url = f"{settings.SENSENOVA_API_BASE}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.SENSENOVA_API_KEY}",
        "Content-Type": "application/json",
    }

    system_prompt = """你是一个智能助手，运行在 AI 报表生成平台中。你可以：
- 与用户自由对话，回答各种问题
- 帮助用户分析数据、提供建议
- 解释图表和数据相关的概念
- 提供 Excel 和数据分析方面的帮助

请用中文回复，保持友好、专业的语气。回答简洁清晰。"""

    data = {
        "model": settings.SENSENOVA_PROMPT_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": request.message},
        ],
        "temperature": 0.8,
        "max_tokens": 2000,
    }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()

            if "choices" in result and len(result["choices"]) > 0:
                reply = result["choices"][0]["message"]["content"]

                # 保存聊天记录
                try:
                    save_chat(db=db, user_message=request.message, ai_reply=reply)
                except Exception as e:
                    print(f"保存聊天记录失败: {e}")

                return create_camel_response({"reply": reply})
            else:
                raise HTTPException(status_code=500, detail="AI 返回格式错误")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"AI 服务调用失败: {e.response.status_code}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"聊天服务异常: {str(e)}")


# ── 聊天历史记录 ──


@router.get("/history")
async def get_chat_history(db: Session = Depends(get_db)):
    """获取聊天历史记录列表"""
    records = get_chat_list(db)
    data = [
        {
            "id": str(r.id),
            "title": r.title or r.user_message[:30],
            "user_message": r.user_message,
            "ai_reply": r.ai_reply,
            "created_at": r.created_at.isoformat() if r.created_at else "",
        }
        for r in records
    ]
    return create_camel_response({"data": data})


@router.get("/history/{history_id}")
async def get_chat_history_detail(history_id: int, db: Session = Depends(get_db)):
    """获取单条聊天记录"""
    record = get_chat_detail(db, history_id)
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    return create_camel_response({
        "id": str(record.id),
        "title": record.title,
        "user_message": record.user_message,
        "ai_reply": record.ai_reply,
        "created_at": record.created_at.isoformat() if record.created_at else "",
    })


@router.delete("/history/{history_id}")
async def delete_chat_history(history_id: int, db: Session = Depends(get_db)):
    """删除聊天记录"""
    ok = delete_chat(db, history_id)
    if not ok:
        raise HTTPException(status_code=404, detail="记录不存在")
    return {"message": "删除成功"}
