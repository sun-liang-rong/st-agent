---
title: Agent-4: 前端交互增强
date: 2026-05-22
agent: agent-4
depends-on: Agent-1 (SSE接口), Agent-2 (Home视觉基础)
blocks: Agent-5 (集成测试)
---

# Agent-4: 前端交互增强

## 目标

在视觉风格基础上，为两个核心页面添加交互增强功能：流式打字、空状态引导、提示词灵感、骨架屏加载等。

## 改动文件

| 文件 | 改动类型 | 说明 |
|------|---------|------|
| `frontend/src/pages/Home.vue` | 修改 | 流式渲染、空状态、加载反馈 |
| `frontend/src/pages/ImageGen.vue` | 修改 | 提示词灵感、骨架屏加载 |
| `frontend/src/services/api.ts` | 修改 | 新增 SSE 流式调用方法 |
| `frontend/src/style.css` | 修改 | 新增骨架屏流光动画 |

## 前置依赖

- **Agent-1** 完成后：`POST /api/v1/chat/stream` SSE 端点可用
- **Agent-2** 完成后：Home.vue 已有温暖活泼视觉基础

## 详细任务

### 1. SSE 流式调用方法

文件：`frontend/src/services/api.ts`

新增 `chatStream` 方法：

```typescript
chatStream(
  message: string,
  contextId?: string,
  onToken: (token: string) => void,
  onDone: (contextId: string) => void,
  onError: (error: string) => void,
): void {
  const token = localStorage.getItem('access_token')
  const body = JSON.stringify({ message, contextId })

  fetch('/api/v1/chat/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body,
  }).then(async (response) => {
    if (!response.ok) {
      onError(`HTTP ${response.status}`)
      return
    }

    const reader = response.body!.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = JSON.parse(line.slice(6))
          // 根据 event type 处理
          if (data.content) onToken(data.content)
          if (data.contextId) onDone(data.contextId)
          if (data.message) onError(data.message)
        }
      }
    }
  }).catch((e) => onError(e.message))
}
```

### 2. Home.vue 流式打字效果

文件：`frontend/src/pages/Home.vue`

改造 `send()` 方法：

```typescript
async function send() {
  const content = input.value.trim()
  if (!content || loading.value) return

  // 添加用户消息
  messages.value.push({
    id: `${Date.now()}-u`,
    role: 'user',
    content,
    created_at: new Date().toISOString(),
  })
  input.value = ''
  loading.value = true

  // 创建 AI 消息占位
  const aiMsgId = `${Date.now()}-a`
  messages.value.push({
    id: aiMsgId,
    role: 'assistant',
    content: '',
    created_at: new Date().toISOString(),
    isStreaming: true,
  })

  const aiMsg = messages.value[messages.value.length - 1]

  apiService.chatStream(
    content,
    sessionId.value || undefined,
    (token) => {
      aiMsg.content += token
    },
    (contextId) => {
      sessionId.value = contextId
      aiMsg.isStreaming = false
      loading.value = false
      sessionStore.loadSessions()
    },
    (error) => {
      aiMsg.content = `出错了：${error}`
      aiMsg.isStreaming = false
      loading.value = false
    },
  )
}
```

模板中流式消息显示光标：

```html
<div v-if="msg.isStreaming" class="streaming-cursor">
  {{ msg.content }}<span class="cursor-blink">▊</span>
</div>
<div v-else>
  <MarkdownRenderer :content="msg.content" />
</div>
```

### 3. Home.vue 空状态引导

```html
<div v-if="messages.length === 0" class="flex flex-col items-center justify-center py-16 text-center">
  <div class="text-5xl mb-4">🗺️</div>
  <div class="text-xl font-semibold text-amber-800 dark:text-amber-200 mb-2">你好呀！想探索哪里？</div>
  <div class="text-sm text-amber-600 dark:text-amber-400 mb-6">告诉我你的目的地，我来帮你规划完美旅程</div>
  <div class="flex gap-3 flex-wrap justify-center">
    <button @click="quickSend('帮我规划一个杭州三日游')"
      class="bg-white dark:bg-stone-800 border-2 border-amber-300 dark:border-stone-600 rounded-full px-4 py-2 text-sm text-amber-800 dark:text-amber-200 hover:-translate-y-0.5 hover:shadow-md transition-all">
      🏞️ 杭州三日游
    </button>
    <button @click="quickSend('帮我规划成都美食之旅')"
      class="bg-white dark:bg-stone-800 border-2 border-amber-300 dark:border-stone-600 rounded-full px-4 py-2 text-sm text-amber-800 dark:text-amber-200 hover:-translate-y-0.5 hover:shadow-md transition-all">
      🌸 成都美食之旅
    </button>
    <button @click="quickSend('帮我规划云南自驾游')"
      class="bg-white dark:bg-stone-800 border-2 border-amber-300 dark:border-stone-600 rounded-full px-4 py-2 text-sm text-amber-800 dark:text-amber-200 hover:-translate-y-0.5 hover:shadow-md transition-all">
      🏔️ 云南自驾游
    </button>
  </div>
</div>
```

新增 `quickSend` 方法：

```typescript
function quickSend(text: string) {
  input.value = text
  send()
}
```

### 4. Home.vue 发送加载反馈

发送按钮改造：

```html
<button :disabled="loading || !input.trim()" @click="send"
  class="px-4 py-2 rounded-xl bg-gradient-to-r from-amber-500 to-red-500 text-white disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2">
  <svg v-if="loading" class="w-4 h-4 animate-spin" ...>...</svg>
  {{ loading ? '思考中...' : '发送' }}
</button>
```

输入框在 loading 时 disabled：

```html
<textarea :disabled="loading" ...>
```

### 5. ImageGen.vue 提示词灵感

输入区上方添加灵感标签：

```html
<div v-if="items.length === 0" class="flex gap-2 flex-wrap mb-3">
  <button @click="fillPrompt('日落下的古镇，水墨画风格')"
    class="bg-white dark:bg-stone-800 border-2 border-amber-300 dark:border-stone-600 rounded-full px-3 py-1.5 text-xs text-amber-800 dark:text-amber-200 hover:-translate-y-0.5 hover:shadow-md transition-all">
    🌅 日落古镇
  </button>
  <button @click="fillPrompt('雪山湖泊倒影，写实摄影')"
    class="...">🏔️ 雪山湖泊</button>
  <button @click="fillPrompt('樱花小径，日系插画')"
    class="...">🌸 樱花小径</button>
</div>
```

```typescript
function fillPrompt(text: string) {
  input.value = text
}
```

### 6. ImageGen.vue 骨架屏加载

生成中在网格中插入骨架卡片：

```html
<!-- 骨架屏卡片 -->
<div v-if="loading" class="bg-white dark:bg-stone-800 border-2 border-dashed border-amber-300 dark:border-stone-600 rounded-2xl overflow-hidden">
  <div class="w-full aspect-square skeleton-shimmer flex items-center justify-center">
    <span class="text-2xl animate-pulse">✨</span>
  </div>
  <div class="p-3">
    <div class="h-4 bg-amber-100 dark:bg-stone-700 rounded skeleton-shimmer w-3/4"></div>
  </div>
</div>
```

### 7. CSS 动画

文件：`frontend/src/style.css`

新增光标闪烁动画：

```css
.cursor-blink {
  animation: blink 1s step-end infinite;
  color: #f59e0b;
}
@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}
```

骨架屏流光动画（已有 `skeleton-shimmer`，确认可用即可）。

## 约束

- 不修改后端代码（依赖 Agent-1 的 SSE 端点）
- 不修改视觉风格（依赖 Agent-2 的基础）
- 保留非流式模式作为 fallback：如果 SSE 不可用，回退到原有 `POST /chat` 接口
- `MarkdownRenderer` 组件在流式完成后使用，流式中显示纯文本+光标

## 自测清单

- [ ] 发送消息后 AI 回复逐字出现，带闪烁光标
- [ ] 流式完成后光标消失，内容切换为 Markdown 渲染
- [ ] 空状态显示大 emoji + 欢迎语 + 3个快捷按钮
- [ ] 快捷按钮点击后自动发送消息
- [ ] 发送时按钮显示"思考中..." + 旋转动画
- [ ] 发送时输入框 disabled
- [ ] 图片生成页显示提示词灵感标签
- [ ] 灵感标签点击填入输入框
- [ ] 图片生成中显示骨架屏卡片 + ✨ 脉冲
- [ ] SSE 连接错误时显示错误提示，不崩溃
- [ ] 暗色模式下所有新增元素正常

## 测试方法

```bash
# 确保后端 SSE 端点已部署（Agent-1 完成）
cd backend && python -m uvicorn app.main:app

# 启动前端
cd frontend && npm run dev
```

1. 打开聊天页面，检查空状态引导
2. 点击快捷按钮，验证自动发送
3. 发送消息，观察流式打字效果
4. 等待流式完成，检查 Markdown 渲染切换
5. 打开图片生成页面，检查灵感标签
6. 点击灵感标签，验证填入输入框
7. 生成图片，观察骨架屏动画
8. 模拟网络错误，检查 fallback 和错误提示