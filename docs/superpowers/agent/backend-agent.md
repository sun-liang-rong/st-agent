---
title: ST-Agent 任务分工 — 后端 Agent
created: 2026-05-23
role: backend
scope: API / 数据库 / 服务层
---

# 后端 Agent 任务分工

## 职责边界

- 所有 API 端点的设计与实现
- 数据库模型、迁移脚本
- 业务服务层逻辑
- 认证与安全
- 不涉及前端页面、组件、样式

---

## P0 阶段（第 1-2 周）

### T-B01: Alembic 数据库迁移初始化

| 项目 | 内容 |
|------|------|
| 优先级 | 最高，阻塞后续所有数据库变更 |
| 预计工时 | 0.5 天 |
| 依赖 | 无 |
| 交付物 | `alembic.ini`, `alembic/env.py`, 初始迁移脚本 |

**任务清单**：
- [ ] `pip install alembic`，添加到 `requirements.txt`
- [ ] 在 `backend/` 目录执行 `alembic init alembic`
- [ ] 配置 `alembic/env.py`：导入 `Base.metadata`，读取 `config.py` 数据库 URL
- [ ] 执行 `alembic revision --autogenerate -m "initial"` 生成初始迁移
- [ ] 验证 `alembic upgrade head` 可正常建表
- [ ] 移除 `main.py` 中的 `Base.metadata.create_all(bind=engine)`
- [ ] 在 `main.py` startup 事件中添加 `alembic upgrade head` 调用（或文档化为手动步骤）

### T-B02: 对话中生成图片 — 后端

| 项目 | 内容 |
|------|------|
| 优先级 | P0 |
| 预计工时 | 2 天 |
| 依赖 | T-B01（需要 Alembic 就绪） |
| 交付物 | SSE 事件流扩展，图片生成意图检测 |

**任务清单**：
- [ ] 在 `ai_service.py` 中新增 `detect_image_intent(user_message) -> bool` 方法
  - 关键词匹配：生成图片、画一张、看看什么样、图片、画等
  - 或让 AI 在 system prompt 中判断是否需要生成图片
- [ ] 修改 `chat_stream` 逻辑：
  - 检测到图片意图时，先输出 `image_intent` 事件
  - 调用 `generate_image()` 获取图片 URL
  - 中间输出 `image_progress` 事件（构思画面/生成图片/下载完成）
  - 输出 `image_result` 事件（包含 imageUrl, contextId）
  - 继续输出文字回复
- [ ] SSE 事件格式定义：
  ```
  event: image_intent
  data: {"message": "正在为你生成图片..."}

  event: image_progress
  data: {"step": 1, "message": "正在构思画面..."}

  event: image_result
  data: {"imageUrl": "/generated/xxx.png", "contextId": "chat-xxx"}
  ```
- [ ] 保存图片生成记录到 `chat_histories`（image_url 字段）
- [ ] 编写单元测试

### T-B03: 消息重新生成 — 后端

| 项目 | 内容 |
|------|------|
| 优先级 | P0 |
| 预计工时 | 1 天 |
| 依赖 | 无 |
| 交付物 | `POST /api/v1/chat/regenerate/{message_id}` 端点 |

**任务清单**：
- [ ] 新增 API 端点 `POST /api/v1/chat/regenerate/{message_id}`
  - 根据 message_id 查找原始记录
  - 提取 user_message 字段
  - 调用 AI 服务重新生成回复（流式）
  - 更新原记录的 ai_reply 字段
- [ ] 在 `chat_history_service.py` 中新增 `regenerate_message(message_id, user_id)` 方法
- [ ] 权限校验：message_id 归属当前用户
- [ ] SSE 流式返回（与 chat/stream 相同格式）
- [ ] 编写单元测试

---

## P1 阶段（第 3-4 周）

### T-B04: 会话搜索 — 后端

| 项目 | 内容 |
|------|------|
| 优先级 | P1 |
| 预计工时 | 1 天 |
| 依赖 | T-B01 |
| 交付物 | `GET /api/v1/chat/sessions/search` 端点 |

**任务清单**：
- [ ] 新增 `GET /api/v1/chat/sessions/search?q=keyword&limit=20`
- [ ] 搜索范围：title + user_message + ai_reply（LIKE 或 FULLTEXT）
- [ ] 返回匹配的会话列表（按时间倒序）
- [ ] 高效查询：考虑添加 FULLTEXT 索引
  - Alembic 迁移：`CREATE FULLTEXT INDEX idx_chat_search ON chat_histories(title, user_message, ai_reply)`
- [ ] 分页支持
- [ ] 编写单元测试

### T-B05: 攻略导出 — 后端

| 项目 | 内容 |
|------|------|
| 优先级 | P1 |
| 预计工时 | 2 天 |
| 依赖 | T-B01 |
| 交付物 | `POST /api/v1/travel/export` 端点，PDF/图片生成 |

**任务清单**：
- [ ] 新增 `POST /api/v1/travel/export`
  - 请求参数：`{"contextId": "xxx", "format": "pdf" | "image"}`
  - 根据 contextId 查找攻略内容
- [ ] 新建 `backend/app/services/export_service.py`
  - `export_to_pdf(content, output_path)` — 使用 weasyprint
  - `export_to_image(content, output_path)` — 使用 imgkit 或 playwright
- [ ] PDF 模板设计：
  - 品牌 Logo + 渐变标题栏
  - 分段排版（行程概览、每日行程、美食推荐等）
  - 支持嵌入图片
- [ ] 返回文件流（`StreamingResponse`），设置 `Content-Disposition`
- [ ] 添加依赖：`weasyprint`, `imgkit` 到 `requirements.txt`
- [ ] 编写单元测试

### T-B06: 软删除与回收站 — 后端

| 项目 | 内容 |
|------|------|
| 优先级 | P1 |
| 预计工时 | 1.5 天 |
| 依赖 | T-B01 |
| 交付物 | 软删除逻辑，回收站 API |

**任务清单**：
- [ ] Alembic 迁移：`chat_histories` 表添加字段
  - `is_deleted` Boolean, default=False
  - `deleted_at` DateTime, nullable=True
- [ ] 修改 `chat_history_service.py`：
  - `delete_session()` → 软删除（设置 is_deleted=True, deleted_at=now）
  - 所有查询方法添加 `is_deleted=False` 过滤
  - 新增 `get_deleted_sessions(user_id)` — 获取回收站列表
  - 新增 `restore_session(context_id, user_id)` — 恢复会话
  - 新增 `permanent_delete_session(context_id, user_id)` — 永久删除
  - 新增 `clear_trash(user_id)` — 清空回收站
- [ ] 新增 API 端点：
  - `GET /api/v1/chat/trash` — 回收站列表
  - `POST /api/v1/chat/trash/{context_id}/restore` — 恢复
  - `DELETE /api/v1/chat/trash/{context_id}` — 永久删除
  - `DELETE /api/v1/chat/trash` — 清空回收站
- [ ] 定时任务：软删除超过 30 天自动永久删除（可用 APScheduler 或 Celery）
- [ ] 编写单元测试

### T-B07: 遗留模块清理

| 项目 | 内容 |
|------|------|
| 优先级 | P1（技术债） |
| 预计工时 | 0.5 天 |
| 依赖 | 确认前端已移除对应调用 |
| 交付物 | 删除无用代码 |

**任务清单**：
- [ ] 删除 `backend/app/api/upload.py`
- [ ] 删除 `backend/app/api/generate.py`
- [ ] 删除 `backend/app/api/task.py`
- [ ] 删除 `backend/app/api/sse.py`
- [ ] 删除 `backend/app/api/history.py`
- [ ] 从 `backend/app/api/__init__.py` 移除对应路由注册
- [ ] 删除 `backend/app/services/task.py`
- [ ] 删除 `backend/app/services/history.py`
- [ ] 从 `requirements.txt` 移除不再需要的依赖（celery, redis, pandas, openpyxl, numpy, boto3, minio）
- [ ] 删除 `backend/app/models/report_history.py`（确认无引用后）
- [ ] 验证应用启动正常

---

## P2 阶段（第 5-6 周）

### T-B08: 用户个人中心 — 后端

| 项目 | 内容 |
|------|------|
| 优先级 | P2 |
| 预计工时 | 1.5 天 |
| 依赖 | T-B01 |
| 交付物 | 个人信息编辑 + 密码修改 API |

**任务清单**：
- [ ] `PUT /api/v1/auth/profile` — 更新个人信息
  - 请求参数：`{"full_name": "xxx", "email": "xxx", "avatar_url": "xxx"}`
  - 邮箱唯一性校验
- [ ] `PUT /api/v1/auth/password` — 修改密码
  - 请求参数：`{"old_password": "xxx", "new_password": "xxx"}`
  - 验证旧密码
  - 新密码强度校验（>=8位，含数字+字母）
- [ ] `POST /api/v1/auth/avatar` — 头像上传
  - 文件大小限制（2MB）
  - 格式限制（jpg, png, webp）
  - 存储到 `uploads/avatars/` 目录
- [ ] Alembic 迁移：`users` 表添加 `avatar_url` 字段
- [ ] 编写单元测试

### T-B09: 图片收藏夹 — 后端

| 项目 | 内容 |
|------|------|
| 优先级 | P2 |
| 预计工时 | 1 天 |
| 依赖 | T-B01 |
| 交付物 | 收藏 CRUD API |

**任务清单**：
- [ ] 新增 `image_favorites` 模型：
  ```python
  id, user_id(FK), image_url, prompt, style, ratio, created_at
  ```
- [ ] Alembic 迁移脚本
- [ ] API 端点：
  - `GET /api/v1/image/favorites` — 收藏列表（分页）
  - `POST /api/v1/image/favorites` — 添加收藏
  - `DELETE /api/v1/image/favorites/{id}` — 取消收藏
  - `POST /api/v1/image/favorites/batch-download` — 批量下载（打包 zip）
- [ ] 防重复收藏：同一用户 + 同一 image_url 唯一约束
- [ ] 编写单元测试

### T-B10: 攻略/图片分享 — 后端

| 项目 | 内容 |
|------|------|
| 优先级 | P2 |
| 预计工时 | 1.5 天 |
| 依赖 | T-B01 |
| 交付物 | 分享链接生成与访问 API |

**任务清单**：
- [ ] 新增 `shares` 模型：
  ```python
  id, user_id(FK), type("travel"|"image"), content_id,
  token(UUID, unique), expires_at, view_count, created_at
  ```
- [ ] Alembic 迁移脚本
- [ ] API 端点：
  - `POST /api/v1/share` — 创建分享
    - 参数：`{"type": "travel"|"image", "content_id": "xxx", "expires_in_hours": 72}`
    - 返回：`{"share_url": "/share/{token}", "token": "xxx"}`
  - `GET /api/v1/share/{token}` — 访问分享内容（无需认证）
    - 增加 view_count
    - 检查 expires_at，过期返回 410
  - `DELETE /api/v1/share/{token}` — 取消分享（需认证，仅创建者）
  - `GET /api/v1/share/mine` — 我的分享列表
- [ ] 编写单元测试

---

## 时间线总览

```
Week 1:  T-B01(Alembic) → T-B02(对话生图) → T-B03(重新生成)
Week 2:  T-B02收尾 + T-B03收尾
Week 3:  T-B04(搜索) + T-B05(导出) + T-B06(软删除)
Week 4:  T-B06收尾 + T-B07(遗留清理)
Week 5:  T-B08(个人中心) + T-B09(收藏夹)
Week 6:  T-B10(分享功能)
```

## 通用规范

- 所有新端点需添加 Pydantic 请求/响应模型
- 所有数据库变更必须通过 Alembic 迁移
- 认证端点使用 `Depends(get_current_user)`
- 错误响应统一使用 `HTTPException` + 标准错误格式
- 服务层方法需编写单元测试（pytest）
