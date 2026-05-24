---
title: ST-Agent 功能增强开发计划
created: 2026-05-23
status: planning
priority_order: P0 > P1 > P2
---

# ST-Agent 功能增强开发计划

## 优先级定义

| 级别 | 含义 | 时间要求 |
|------|------|----------|
| P0 | 核心体验断点，必须优先解决 | 第 1-2 周 |
| P1 | 重要功能缺失，影响产品完整度 | 第 3-4 周 |
| P2 | 锦上添花，提升竞争力 | 第 5-6 周 |

---

## P0 — 核心体验修复（第 1-2 周）

### 1. 对话中生成图片

**问题**：对话页和图片生成页完全割裂，用户聊天时想看图必须切页面，体验断裂。

**方案**：
- 在对话页输入框添加风格/比例选择器（折叠式，默认隐藏）
- 新增 `/api/v1/chat/stream` 的图片生成事件类型
- AI 回复中可嵌入图片卡片（类似 ChatGPT 的图片展示）
- 后端 `chat_stream` 中检测图片生成意图，调用 `ai_service.generate_image`
- SSE 事件流扩展：`image_intent` → `image_progress` → `image_result`

**涉及文件**：
- `backend/app/api/chat.py` — 流式对话增加图片事件
- `backend/app/services/ai_service.py` — 对话中调用图片生成
- `frontend/src/pages/Home.vue` — 输入框增加风格/比例选择，消息区渲染图片卡片
- `frontend/src/services/api.ts` — 解析新增 SSE 事件类型

### 2. 消息重新生成

**问题**：AI 产品标配功能缺失，用户对回复不满意无法重新生成。

**方案**：
- AI 消息气泡底部添加"重新生成"按钮（hover 显示）
- 后端新增 `POST /api/v1/chat/regenerate/{message_id}`
- 重新生成时保留原始用户消息，替换 AI 回复
- 流式输出覆盖原消息，动画效果与首次生成一致
- 侧边栏会话列表无需刷新（contextId 不变）

**涉及文件**：
- `backend/app/api/chat.py` — 新增 regenerate 端点
- `backend/app/services/chat_history_service.py` — 更新指定 AI 回复
- `frontend/src/pages/Home.vue` — 重新生成按钮 + 交互逻辑
- `frontend/src/services/api.ts` — 新增 regenerate API

### 3. Alembic 数据库迁移

**问题**：表结构变更靠 `Base.metadata.create_all`，生产环境修改字段/加索引有数据丢失风险。

**方案**：
- 引入 Alembic，初始化迁移环境
- 基于当前模型生成初始迁移脚本
- 移除 `main.py` 中的 `Base.metadata.create_all`
- 添加 `alembic upgrade head` 到启动流程
- 文档化迁移操作规范

**涉及文件**：
- `backend/alembic.ini` — 新建
- `backend/alembic/` — 新建迁移目录
- `backend/app/main.py` — 移除 create_all
- `backend/requirements.txt` — 添加 alembic 依赖

---

## P1 — 重要功能补全（第 3-4 周）

### 4. 会话搜索

**问题**：历史会话只能滚动浏览，无法按关键词查找，会话多时效率极低。

**方案**：
- 侧边栏顶部添加搜索框
- 后端新增 `GET /api/v1/chat/sessions/search?q=keyword`
- 搜索范围：会话标题 + 用户消息 + AI 回复
- 数据库层面添加 FULLTEXT 索引（title, user_message, ai_reply）
- 前端实时搜索（debounce 300ms），搜索结果高亮匹配关键词

**涉及文件**：
- `backend/app/api/chat.py` — 新增搜索端点
- `backend/app/services/chat_history_service.py` — 搜索逻辑
- `frontend/src/App.vue` — 侧边栏搜索框
- `frontend/src/stores/session.ts` — 搜索状态管理
- `frontend/src/services/api.ts` — 搜索 API

### 5. 移动端适配

**问题**：272px 固定侧边栏在移动端不可用，整体布局未做响应式。

**方案**：
- 侧边栏改为抽屉式（移动端默认收起，汉堡菜单触发）
- 断点：`<768px` 移动布局，`768-1024px` 平板布局，`>1024px` 桌面布局
- 消息气泡宽度自适应，输入框全宽
- 图片生成页网格列数响应式：1列 → 2列 → 3列
- 触屏手势：左滑打开侧边栏，右滑关闭

**涉及文件**：
- `frontend/src/App.vue` — 侧边栏响应式改造
- `frontend/src/pages/Home.vue` — 移动端对话布局
- `frontend/src/pages/ImageGen.vue` — 图片网格响应式
- `frontend/tailwind.config.js` — 断点配置（如需自定义）

### 6. 攻略导出

**问题**：生成的攻略无法导出，用户无法离线使用或分享给同伴。

**方案**：
- 攻略消息增加"导出"按钮（PDF / 图片 两种格式）
- 后端新增 `POST /api/v1/travel/export`
  - PDF：使用 `weasyprint` 或 `reportlab` 生成
  - 图片：将 HTML 渲染为图片（`playwright` 截图或 `imgkit`）
- 导出模板：带品牌 Logo、渐变标题栏、分段排版
- 前端下载导出文件

**涉及文件**：
- `backend/app/api/travel.py` — 新增导出端点
- `backend/app/services/export_service.py` — 新建导出服务
- `backend/requirements.txt` — 添加 weasyplay/reportlab 依赖
- `frontend/src/pages/Home.vue` — 导出按钮 + 下载逻辑
- `frontend/src/services/api.ts` — 导出 API

### 7. 软删除与回收站

**问题**：会话删除为硬删除，误删无法恢复。

**方案**：
- `chat_histories` 表添加 `is_deleted` 字段和 `deleted_at` 字段
- 删除操作改为软删除（`is_deleted=True`）
- 侧边栏新增"回收站"入口，展示已删除会话
- 回收站支持：恢复会话 / 永久删除 / 清空回收站
- 自动清理：软删除超过 30 天的记录自动永久删除（定时任务）
- 现有查询全部添加 `is_deleted=False` 过滤

**涉及文件**：
- `backend/app/models/chat_history.py` — 添加字段
- `backend/alembic/` — 迁移脚本
- `backend/app/services/chat_history_service.py` — 软删除逻辑
- `backend/app/api/chat.py` — 新增回收站端点
- `frontend/src/App.vue` — 回收站入口
- `frontend/src/stores/session.ts` — 回收站状态

---

## P2 — 体验提升（第 5-6 周）

### 8. 用户个人中心

**方案**：
- 新增 `/settings` 页面（当前未注册路由，可复用 Settings.vue）
- 个人信息编辑：头像上传、昵称、邮箱
- 密码修改（需验证旧密码）
- 偏好设置：默认风格、默认比例、语言
- 后端新增 `PUT /api/v1/auth/profile` 和 `PUT /api/v1/auth/password`

**涉及文件**：
- `backend/app/api/auth.py` — 新增端点
- `backend/app/services/user_service.py` — 个人信息/密码更新
- `frontend/src/pages/Settings.vue` — 改造为完整个人中心
- `frontend/src/router/` — 注册路由

### 9. 图片收藏夹

**方案**：
- 新增 `image_favorites` 表（user_id, image_url, prompt, style, ratio, created_at）
- 图片卡片增加收藏按钮（星标图标）
- 新增"我的收藏"页面，网格展示收藏图片
- 支持取消收藏、批量下载
- 后端 CRUD：`GET/POST/DELETE /api/v1/image/favorites`

**涉及文件**：
- `backend/app/models/` — 新增收藏模型
- `backend/app/api/image.py` — 收藏端点
- `frontend/src/pages/ImageGen.vue` — 收藏按钮
- `frontend/src/pages/Favorites.vue` — 新建收藏页
- `frontend/src/router/` — 注册路由

### 10. 攻略/图片分享

**方案**：
- 生成分享链接（带有效期，类似网盘分享）
- 新增 `shares` 表（id, user_id, type, content_id, token, expires_at, view_count）
- 后端新增 `POST /api/v1/share` 创建分享，`GET /api/v1/share/{token}` 访问
- 前端分享弹窗：复制链接 / 生成二维码
- 分享页面：无需登录即可查看攻略/图片（独立布局）

**涉及文件**：
- `backend/app/models/` — 新增分享模型
- `backend/app/api/share.py` — 新建分享路由
- `frontend/src/pages/Home.vue` — 分享按钮
- `frontend/src/pages/ImageGen.vue` — 分享按钮
- `frontend/src/pages/ShareView.vue` — 新建分享查看页

---

## 技术债务（穿插在各阶段）

| 项目 | 归属阶段 | 说明 |
|------|----------|------|
| Alembic 迁移 | P0 | 优先完成，后续所有数据库变更依赖此 |
| 单元测试 | P1 | 核心服务（ai_service, chat_history_service）测试覆盖 |
| 遗留模块清理 | P1 | 删除 upload.py, generate.py, task.py, sse.py, history.py 及对应前端组件 |
| CI/CD | P2 | GitHub Actions：lint + test + build |
| 日志与监控 | P2 | 结构化日志，错误追踪（Sentry 集成） |

---

## 里程碑总览

```
Week 1-2  ── P0 ── 对话中生成图片 + 消息重新生成 + Alembic
Week 3-4  ── P1 ── 会话搜索 + 移动端适配 + 攻略导出 + 软删除
Week 5-6  ── P2 ── 个人中心 + 图片收藏 + 分享功能
贯穿全程  ── 技术债 ── 测试 / 清理 / CI
```

每个功能开发完成后，应同步更新 `xuqiu.md` 需求文档。
