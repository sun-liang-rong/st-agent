---
title: Agent-1: 后端 SSE 流式接口
date: 2026-05-22
agent: agent-1
depends-on: 无
blocks: Agent-4 (前端流式渲染依赖此接口)
---

# Agent-1: 后端 SSE 流式接口

## 目标

为 chat API 添加 SSE 流式响应模式，前端可逐 token 接收 AI 回复。

## 改动文件

| 文件 | 改动类型 | 说明 |
|------|---------|------|
| `backend/app/api/chat.py` | 修改 | 新增 `/chat/stream` SSE 端点 |
| `backend/app/services/chat_history_service.py` | 修改 | 新增流式生成方法 |
| `backend/app/api/__init__.py` | 修改 | 注册新路由 |

## 详细任务

### 1. 新增 SSE 流式端点

文件：`backend/app/api/chat.py`

在现有 `POST /chat` 旁边新增 `POST /chat/stream`：

```python
@router.post("/chat/stream")
async def chat_stream(request: ChatRequest, db: Session = Depends(get_db)):
```

返回 `StreamingResponse`，media_type 为 `text/event-stream`。

### 2. SSE 事件格式

```
event: token
data: {"content": "你好"}

event: token
data: {"content": "！"}

event: done
data: {"contextId": "abc123", "messageId": "msg456"}
```

- `token` 事件：每个 AI 生成的文本片段
- `done` 事件：生成完成，返回 contextId 和 messageId
- 错误时发送 `event: error\ndata: {"message": "xxx"}\n\n` 然后关闭

### 3. 流式生成方法

文件：`backend/app/services/chat_history_service.py`

新增 `stream_chat_message` 方法：
- 调用 AI 服务时使用流式模式（stream=True）
- 用 `async for` 逐 chunk 产出 token
- 生成完成后，将完整消息存入数据库（与现有 `create_chat_message` 逻辑一致）
- 返回 contextId 和 messageId

### 4. 路由注册

文件：`backend/app/api/__init__.py`

确保新端点被正确注册到 router。

## 约束

- 不修改现有 `POST /chat` 端点的行为，保持向后兼容
- 流式端点复用现有的 `ChatRequest` 模型
- 数据库写入在流式完成后一次性执行，不在每个 token 时写入
- SSE 连接断开时需要清理资源

## 自测清单

- [ ] `POST /api/v1/chat/stream` 返回 `text/event-stream`
- [ ] 逐 token 收到 `event: token` 事件
- [ ] 生成结束收到 `event: done` 事件，包含 contextId
- [ ] 流式完成后数据库中有完整的聊天记录
- [ ] 现有 `POST /chat` 非流式端点不受影响
- [ ] AI 服务异常时返回 `event: error` 并正常关闭连接
- [ ] 客户端断开连接后服务端不泄漏资源

## 测试方法

```bash
# 启动后端
cd backend && python -m uvicorn app.main:app

# 测试流式端点（需要有效 token）
curl -N -X POST http://localhost:8000/api/v1/chat/stream \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"message": "你好", "context_id": ""}'

# 测试原端点仍正常
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"message": "你好", "context_id": ""}'
```
