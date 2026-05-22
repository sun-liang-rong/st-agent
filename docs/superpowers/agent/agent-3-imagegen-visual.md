---
title: Agent-3: ImageGen.vue 视觉风格
date: 2026-05-22
agent: agent-3
depends-on: 无
blocks: Agent-4 (交互增强依赖视觉基础)
---

# Agent-3: ImageGen.vue 视觉风格

## 目标

将图片生成页面从冷色调改为温暖活泼风格，包括背景、卡片、输入区的视觉更新，以及画廊布局改造。

## 改动文件

| 文件 | 改动类型 | 说明 |
|------|---------|------|
| `frontend/src/pages/ImageGen.vue` | 修改 | 全面更新模板和样式 |

## 当前状态分析

ImageGen.vue 当前状态：
- 背景：`bg-gray-50 dark:bg-gray-900`
- 图片卡片：`bg-white border rounded-xl`，简单列表布局
- 输入区：`border-gray-300`，生成按钮 `bg-indigo-600`
- 无提示词灵感
- 无操作按钮
- 无加载动画

## 详细任务

### 1. 页面背景

```html
<!-- 当前 -->
<div class="flex flex-col h-full bg-gray-50 dark:bg-gray-900">

<!-- 改为 -->
<div class="flex flex-col h-full bg-gradient-to-br from-amber-50 via-orange-50 to-yellow-50 dark:from-stone-900 dark:via-stone-800 dark:to-stone-900">
```

### 2. 画廊布局

将图片从列表改为网格：

```html
<!-- 当前 -->
<div class="space-y-4">
  <div v-for="it in items" class="bg-white border rounded-xl p-4 space-y-3">

<!-- 改为 -->
<div class="grid grid-cols-2 md:grid-cols-3 gap-4">
  <div v-for="it in items" class="bg-white dark:bg-stone-800 border-2 border-amber-300 dark:border-stone-600 rounded-2xl overflow-hidden shadow-sm hover:shadow-md hover:scale-[1.02] transition-all duration-200 group">
```

### 3. 图片卡片内容

每个卡片内部结构：

```html
<div class="relative">
  <!-- 图片 -->
  <img v-if="it.imageUrl" :src="it.imageUrl"
    class="w-full aspect-square object-cover" alt="generated" />

  <!-- 空状态占位 -->
  <div v-else class="w-full aspect-square bg-gradient-to-br from-amber-100 to-orange-100 dark:from-stone-700 dark:to-stone-600 flex items-center justify-center text-4xl">
    🎨
  </div>

  <!-- hover 操作按钮 -->
  <div v-if="it.imageUrl" class="absolute bottom-3 right-3 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
    <button @click="downloadImage(it.imageUrl)" class="w-8 h-8 rounded-full bg-white/90 dark:bg-stone-700/90 shadow flex items-center justify-center text-sm hover:bg-white">
      ⬇️
    </button>
    <button @click="regenerate(it.prompt)" class="w-8 h-8 rounded-full bg-white/90 dark:bg-stone-700/90 shadow flex items-center justify-center text-sm hover:bg-white">
      🔄
    </button>
  </div>
</div>

<!-- 提示词 -->
<div class="p-3">
  <p class="text-sm text-amber-800 dark:text-amber-200 truncate">{{ it.prompt }}</p>
</div>
```

### 4. 输入区

```html
<!-- 当前 -->
<div class="border-gray-300 ...">
  <button class="bg-indigo-600 ...">

<!-- 改为 -->
<div class="border-2 border-amber-300 dark:border-stone-600 bg-white dark:bg-stone-800 rounded-2xl ...">
  <button class="bg-gradient-to-r from-amber-500 to-red-500 hover:from-amber-600 hover:to-red-600 ...">
```

### 5. 空状态提示

```html
<!-- 当前 -->
<div class="text-gray-400 text-sm">输入提示词，生成图片</div>

<!-- 改为 -->
<div class="flex flex-col items-center justify-center py-16 text-center">
  <div class="text-5xl mb-4">🎨</div>
  <div class="text-lg font-semibold text-amber-800 dark:text-amber-200 mb-2">输入提示词，生成图片</div>
  <div class="text-sm text-amber-600 dark:text-amber-400">试试描述一个场景，我来帮你画出来</div>
</div>
```

### 6. Script 新增方法

```typescript
function downloadImage(url: string) {
  const a = document.createElement('a')
  a.href = url
  a.download = 'ai-generated.png'
  a.click()
}

function regenerate(prompt: string) {
  input.value = prompt
  generate()
}
```

## 约束

- 不改动图片生成逻辑，只改视觉
- 不改动 API 调用
- 不添加提示词灵感标签（Agent-4 负责）
- 不添加骨架屏加载动画（Agent-4 负责）
- 保持暗色模式兼容
- 画廊布局在移动端为 2 列，桌面端为 3 列

## 自测清单

- [ ] 页面背景为暖色渐变
- [ ] 图片以 2-3 列网格展示
- [ ] 图片卡片 amber 边框 + 圆角 + hover 放大效果
- [ ] hover 图片时显示下载和重新生成按钮
- [ ] 下载按钮可正常下载图片
- [ ] 重新生成按钮填入提示词并触发生成
- [ ] 空状态显示大 emoji + 提示文字
- [ ] 输入区 amber 边框 + 渐变生成按钮
- [ ] 暗色模式下所有元素可读且配色协调
- [ ] 移动端 2 列，桌面端 3 列

## 测试方法

```bash
# 启动前端
cd frontend && npm run dev

# 启动后端
cd backend && python -m uvicorn app.main:app
```

1. 浏览器打开 http://localhost:5173/image
2. 输入提示词生成图片
3. 检查画廊网格布局
4. hover 图片检查操作按钮
5. 点击下载验证图片保存
6. 点击重新生成验证功能
7. 切换暗色模式检查
8. 调整浏览器宽度检查响应式布局