---
title: Agent-2: Home.vue 视觉风格
date: 2026-05-22
agent: agent-2
depends-on: 无
blocks: Agent-4 (交互增强依赖视觉基础)
---

# Agent-2: Home.vue 视觉风格

## 目标

将聊天页面从当前冷色调改为温暖活泼风格，包括背景、气泡、头像、输入区的视觉更新。

## 改动文件

| 文件 | 改动类型 | 说明 |
|------|---------|------|
| `frontend/src/pages/Home.vue` | 修改 | 全面更新模板和样式 |
| `frontend/src/style.css` | 修改 | 添加消息动画 keyframes |

## 当前状态分析

Home.vue 当前状态：
- 背景：`bg-gray-50 dark:bg-gray-900`（冷灰色）
- AI 消息：`bg-white dark:bg-gray-800`，无头像，无时间戳
- 用户消息：`bg-indigo-600 text-white`，无头像
- 输入区：`border-gray-300`，发送按钮 `bg-indigo-600`
- 无空状态引导
- 无复制按钮

## 详细任务

### 1. 页面背景

```html
<!-- 当前 -->
<div class="flex flex-col h-full bg-gray-50 dark:bg-gray-900">

<!-- 改为 -->
<div class="flex flex-col h-full bg-gradient-to-br from-amber-50 via-orange-50 to-yellow-50 dark:from-stone-900 dark:via-stone-800 dark:to-stone-900">
```

### 2. AI 消息气泡

```html
<!-- 当前 -->
<div class="bg-white dark:bg-gray-800 rounded-2xl px-4 py-3 ...">

<!-- 改为 -->
<div class="bg-white dark:bg-stone-800 border-2 border-amber-300 dark:border-stone-600 rounded-tl-sm rounded-tr-xl rounded-bl-xl rounded-br-xl px-4 py-3 shadow-sm ...">
```

AI 头像（新增，在气泡左侧）：
```html
<div class="w-9 h-9 rounded-full bg-gradient-to-br from-amber-500 to-red-500 flex items-center justify-center text-lg shadow-md flex-shrink-0">
  🤖
</div>
```

### 3. 用户消息气泡

```html
<!-- 当前 -->
<div class="bg-indigo-600 text-white rounded-2xl px-4 py-3 ...">

<!-- 改为 -->
<div class="bg-gradient-to-r from-amber-500 to-red-500 text-white rounded-tr-sm rounded-tl-xl rounded-bl-xl rounded-br-xl px-4 py-3 shadow-md ...">
```

用户头像（新增，在气泡右侧）：
```html
<div class="w-9 h-9 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-lg shadow-md flex-shrink-0">
  😊
</div>
```

### 4. 时间戳 + 复制按钮

每条消息下方新增：
```html
<div class="flex items-center gap-2 mt-1 ml-12 opacity-0 group-hover:opacity-100 transition-opacity">
  <span class="text-xs text-amber-600 dark:text-amber-400">{{ formatTime(msg.created_at) }}</span>
  <button @click="copyMessage(msg.content)" class="text-xs text-amber-700 dark:text-amber-300 hover:text-amber-900">
    📋 复制
  </button>
</div>
```

需要在 script 中添加：
- `formatTime(date)` 方法：格式化时间为 HH:mm
- `copyMessage(text)` 方法：调用 `navigator.clipboard.writeText`
- 消息容器添加 `group` class 以支持 hover 显示

### 5. 输入区

```html
<!-- 当前 -->
<div class="border-gray-300 ...">
  <button class="bg-indigo-600 ...">

<!-- 改为 -->
<div class="border-2 border-amber-300 dark:border-stone-600 bg-white dark:bg-stone-800 rounded-2xl ...">
  <button class="bg-gradient-to-r from-amber-500 to-red-500 hover:from-amber-600 hover:to-red-600 ...">
```

### 6. 全局动画

文件：`frontend/src/style.css`

添加消息滑入动画：
```css
@keyframes slideIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
.message-enter {
  animation: slideIn 0.3s ease-out;
}
```

## 约束

- 不改动消息发送逻辑，只改视觉
- 不改动 API 调用
- 不添加空状态引导（Agent-4 负责）
- 不添加流式渲染（Agent-4 负责）
- 保持暗色模式兼容
- 保持 `MarkdownRenderer` 组件不变

## 自测清单

- [ ] 页面背景为暖色渐变（亮色 amber-50→orange-50→yellow-50）
- [ ] AI 气泡白底 + amber 边框 + 左上小圆角
- [ ] 用户气泡 amber→red 渐变 + 右上小圆角
- [ ] AI 头像显示🤖，用户头像显示😊
- [ ] hover 消息时显示时间戳和复制按钮
- [ ] 复制按钮可正常复制文本到剪贴板
- [ ] 输入区 amber 边框 + 渐变发送按钮
- [ ] 暗色模式下所有元素可读且配色协调
- [ ] 消息出现时有 slideIn 动画

## 测试方法

```bash
# 启动前端
cd frontend && npm run dev

# 启动后端
cd backend && python -m uvicorn app.main:app
```

1. 浏览器打开 http://localhost:5173
2. 登录后进入聊天页面
3. 发送消息，检查气泡样式、头像、时间戳
4. hover 消息检查复制按钮
5. 点击复制，粘贴验证内容正确
6. 切换暗色模式，检查所有元素
7. 检查消息出现动画
