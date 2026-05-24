---
title: ST-Agent 任务分工 — 协调总览
created: 2026-05-23
type: coordination
---

# ST-Agent Agent 任务协调总览

## Agent 角色定义

| Agent | 职责 | 详细任务 |
|-------|------|----------|
| **后端 Agent** | API、数据库、服务层 | [backend-agent.md](backend-agent.md) |
| **前端 Agent** | 页面、组件、样式、状态管理 | [frontend-agent.md](frontend-agent.md) |

---

## 任务依赖关系

### P0 阶段

```
T-B01(Alembic) ──→ T-B02(对话生图-后端) ──→ T-F01(对话生图-前端)
                 ──→ T-B03(重新生成-后端) ──→ T-F02(重新生成-前端)
```

**关键路径**：Alembic → 对话生图（后端→前端），Alembic 阻塞所有数据库变更。

**并行机会**：
- T-B03（重新生成-后端）不依赖 Alembic，可与 T-B02 并行
- T-F01、T-F02 的 UI 框架部分可提前开发，不依赖后端

### P1 阶段

```
T-B01 ──→ T-B04(搜索-后端)   ──→ T-F03(搜索-前端)
       ──→ T-B05(导出-后端)   ──→ T-F05(导出-前端)
       ──→ T-B06(软删除-后端)  ──→ T-F06(回收站-前端)
T-F04(移动端适配) ← 无后端依赖，可独立进行
T-B07(遗留清理)   ← 纯后端，确认前端已移除调用后进行
```

**并行机会**：
- T-F04（移动端适配）无后端依赖，整个 P1 阶段可随时开始
- T-B04/T-B05/T-B06 可并行开发

### P2 阶段

```
T-B01 ──→ T-B08(个人中心-后端) ──→ T-F07(个人中心-前端)
       ──→ T-B09(收藏夹-后端)   ──→ T-F08(收藏夹-前端)
       ──→ T-B10(分享-后端)     ──→ T-F09(分享-前端)
```

**并行机会**：
- T-B08/T-B09/T-B10 可并行开发
- T-F07/T-F08 可并行开发

---

## 甘特图（6 周）

```
Week 1 │ B01 B02 B03    │ F01* F02*
Week 2 │ B02→ B03→      │ F01→ F02→
Week 3 │ B04 B05 B06    │ F03 F04 F05
Week 4 │ B06→ B07       │ F04→ F06
Week 5 │ B08 B09        │ F07 F08
Week 6 │ B10            │ F09

* F01/F02 的 UI 框架可在 Week 1 提前开发，后端联调在 Week 2
→ 表示延续收尾
```

---

## 联调检查点

| 检查点 | 时间 | 验证内容 |
|--------|------|----------|
| CP1 | Week 2 末 | 对话生图端到端：用户输入→AI检测意图→生成图片→前端展示 |
| CP2 | Week 2 末 | 消息重新生成端到端：点击→流式替换→历史记录更新 |
| CP3 | Week 4 末 | 搜索 + 软删除 + 导出功能联调 |
| CP4 | Week 4 末 | 移动端全流程验证（对话/图片/登录） |
| CP5 | Week 6 末 | 个人中心 + 收藏 + 分享全量联调 |
| CP6 | Week 6 末 | 遗留模块清理后回归测试 |

---

## 共享接口契约

前后端 Agent 通过以下接口契约协作，后端先定义，前端按契约开发：

### 新增 API 汇总

| 方法 | 路径 | 阶段 | 后端任务 | 前端任务 |
|------|------|------|----------|----------|
| POST | `/api/v1/chat/regenerate/{message_id}` | P0 | T-B03 | T-F02 |
| GET | `/api/v1/chat/sessions/search` | P1 | T-B04 | T-F03 |
| POST | `/api/v1/travel/export` | P1 | T-B05 | T-F05 |
| GET | `/api/v1/chat/trash` | P1 | T-B06 | T-F06 |
| POST | `/api/v1/chat/trash/{context_id}/restore` | P1 | T-B06 | T-F06 |
| DELETE | `/api/v1/chat/trash/{context_id}` | P1 | T-B06 | T-F06 |
| DELETE | `/api/v1/chat/trash` | P1 | T-B06 | T-F06 |
| PUT | `/api/v1/auth/profile` | P2 | T-B08 | T-F07 |
| PUT | `/api/v1/auth/password` | P2 | T-B08 | T-F07 |
| POST | `/api/v1/auth/avatar` | P2 | T-B08 | T-F07 |
| GET | `/api/v1/image/favorites` | P2 | T-B09 | T-F08 |
| POST | `/api/v1/image/favorites` | P2 | T-B09 | T-F08 |
| DELETE | `/api/v1/image/favorites/{id}` | P2 | T-B09 | T-F08 |
| POST | `/api/v1/image/favorites/batch-download` | P2 | T-B09 | T-F08 |
| POST | `/api/v1/share` | P2 | T-B10 | T-F09 |
| GET | `/api/v1/share/{token}` | P2 | T-B10 | T-F09 |
| DELETE | `/api/v1/share/{token}` | P2 | T-B10 | T-F09 |
| GET | `/api/v1/share/mine` | P2 | T-B10 | T-F09 |

### SSE 事件扩展（对话生图）

| 事件 | 数据格式 | 说明 |
|------|----------|------|
| `image_intent` | `{"message": "正在为你生成图片..."}` | AI 检测到图片意图 |
| `image_progress` | `{"step": 1, "message": "正在构思画面..."}` | 图片生成进度 |
| `image_result` | `{"imageUrl": "/generated/xxx.png", "contextId": "chat-xxx"}` | 图片生成结果 |

---

## 风险与应对

| 风险 | 影响 | 应对 |
|------|------|------|
| Alembic 迁移与现有数据不兼容 | 阻塞所有后端任务 | T-B01 优先，先在开发环境验证迁移 |
| SenseNova 图片 API 限流 | 对话生图功能不可用 | 保持图片生成页独立入口，对话生图作为增强而非替代 |
| weasyprint 安装依赖系统库 | 攻略导出功能受阻 | 备选方案：使用 reportlab 或前端 html2canvas |
| 移动端适配工作量超预期 | 拖延 P1 整体进度 | 优先适配对话页，图片页次之，设置页可延后 |
| 前后端联调阻塞 | 前端等后端 | 前端先写 UI + mock 数据，后端就绪后联调 |
