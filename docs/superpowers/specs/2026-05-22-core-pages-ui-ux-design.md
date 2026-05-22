---
title: 核心页面 UI/UX 优化
date: 2026-05-22
scope: Home.vue, ImageGen.vue
---

# 核心页面 UI/UX 优化设计

## 风格方向：温暖活泼

暖色调 + 圆润造型 + emoji 点缀，类似豆包/Kimi 风格，亲切友好。

## 色彩体系

| 角色 | 色值 | 用途 |
|------|------|------|
| 主色 Amber | `#f59e0b` | 按钮、用户气泡渐变起点 |
| 强调 Red | `#ef4444` | 用户气泡渐变终点、重要操作 |
| 边框 Yellow | `#fbbf24` | AI 气泡边框、卡片边框 |
| 背景 Warm | `#fffbeb` | 页面底色 |
| 文字 Brown | `#78350f` | 正文文字 |
| 渐变 Accent | Amber→Red | 用户气泡、头像、CTA 按钮 |

暗色模式对应色值：
- 背景：`#1c1917`（stone-900）
- 卡片：`#292524`（stone-800）
- 边框：`#44403c`（stone-700）
- 文字：`#fef3c7`（amber-100）

## 实现策略：渐进式优化

在现有组件上逐步增强，不改文件结构。分三个阶段：

### 阶段一：视觉风格更新

**Home.vue 聊天页面：**
- 页面背景：`bg-gradient-to-br from-amber-50 via-orange-50 to-yellow-50`（暗色：`dark:from-stone-900 dark:via-stone-800 dark:to-stone-900`）
- AI 消息气泡：白底 + `border-2 border-amber-300` + `rounded-tl-sm rounded-tr-xl rounded-bl-xl rounded-br-xl`（左上角小圆角营造对话尾巴），暗色：`dark:bg-stone-800 dark:border-stone-600`
- 用户消息气泡：`bg-gradient-to-r from-amber-500 to-red-500` + `rounded-tr-sm rounded-tl-xl rounded-bl-xl rounded-br-xl`（右上角小圆角）+ 白色文字
- 头像：36px 圆形，AI 用渐变底+emoji🤖，用户用渐变底+emoji😊
- 消息下方：时间戳（小字 amber-600）+ 复制按钮
- 输入区：白底 + `border-2 border-amber-300` + 圆角 `rounded-2xl`，发送按钮用渐变

**ImageGen.vue 图片生成页面：**
- 同样的暖色背景
- 图片卡片：白底 + `border-2 border-amber-300` + `rounded-2xl`
- 生成按钮：渐变 amber→red

### 阶段二：交互增强

**Home.vue：**
1. **流式打字效果** — 后端 chat API 改为 SSE 流式返回，前端逐字渲染 AI 回复，带光标闪烁动画
2. **空状态引导** — 消息为空时显示：大 emoji 🗺️ + 欢迎语"你好呀！想探索哪里？" + 3个快捷提问按钮（杭州三日游/成都美食之旅/云南自驾游），点击直接发送
3. **消息气泡丰富** — 每条消息下方显示时间戳 + 复制按钮（hover 显示），AI 回复支持 Markdown 渲染
4. **发送加载反馈** — 发送时按钮变为旋转动画 + "思考中..."文字，输入框 disabled

**ImageGen.vue：**
1. **提示词灵感** — 输入区上方展示3个示例提示词标签，点击填入输入框
2. **画廊布局** — 图片从列表改为 2-3 列网格（`grid grid-cols-2 md:grid-cols-3`），卡片带圆角和边框
3. **图片操作按钮** — hover 时在图片右下角显示：下载⬇️ + 重新生成🔄 按钮
4. **生成进度动画** — 生成中显示骨架屏卡片，带流光动画 + ✨ 脉冲图标

### 阶段三：动画与细节

- 消息出现动画：`slideIn` 从下方滑入
- 快捷按钮 hover：微微上浮 + 阴影加深
- 图片卡片 hover：轻微放大 `scale-[1.02]` + 阴影加深
- 流式输出光标：1s 闪烁的竖线 `▊`
- 侧边栏会话项 hover：amber-50 背景

## 后端改动

流式打字效果需要后端配合：
- `POST /api/v1/chat` 增加 `stream: bool` 参数
- 当 `stream=true` 时返回 SSE 响应，逐 token 推送
- 事件格式：`event: token\ndata: {"content": "你好"}\n\n`
- 结束事件：`event: done\ndata: {"contextId": "xxx"}\n\n`

## 不做的事

- 不改侧边栏布局（App.vue）
- 不改登录/注册页面
- 不新增路由或页面
- 不拆分组件文件结构
