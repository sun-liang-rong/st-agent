<template>
  <div class="h-full flex flex-col bg-gray-50 dark:bg-slate-900">
    <!-- 消息列表 -->
    <div ref="messageContainer" class="flex-1 overflow-y-auto p-6 space-y-6">
      <!-- 空状态 -->
      <div v-if="messages.length === 0" class="flex flex-col items-center justify-center h-full text-center px-6">
        <div class="w-20 h-20 bg-gradient-to-br from-primary-100 to-primary-200 dark:from-primary-900/40 dark:to-primary-800/30 rounded-2xl flex items-center justify-center mb-6 shadow-inner">
          <svg class="w-10 h-10 text-primary-500 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 1 1 7.072 0l-.548.547A3.374 3.374 0 0 0 14 18.469V19a2 2 0 1 1-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
          </svg>
        </div>
        <h2 class="text-2xl font-bold text-gray-800 dark:text-white mb-2">{{ tt('home.emptyTitle') }}</h2>
        <p class="text-gray-500 dark:text-gray-400 mb-8 max-w-md">{{ tt('home.emptyDesc') }}</p>
        
        <!-- 上传按钮 -->
        <div
          @click="triggerUpload"
          @dragover.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
          @drop.prevent="handleDrop"
          class="w-full max-w-lg cursor-pointer"
        >
          <div
            class="border-2 border-dashed rounded-xl p-12 transition-all duration-300"
            :class="[
              isDragging
                ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20 scale-[1.02] shadow-lg shadow-primary-200 dark:shadow-primary-900/30'
                : 'border-gray-300 dark:border-slate-600 hover:border-primary-500 dark:hover:border-primary-400',
              isUploading ? 'opacity-60 pointer-events-none' : ''
            ]"
          >
            <!-- 上传进度环 -->
            <div v-if="isUploading" class="flex flex-col items-center">
              <svg class="w-14 h-14 text-primary-500 animate-spin mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
              </svg>
              <p class="text-primary-600 dark:text-primary-400 font-medium">正在上传解析...</p>
            </div>
            <!-- 拖拽/点击状态 -->
            <template v-else>
              <svg class="w-12 h-12 mx-auto mb-4 transition-colors" :class="isDragging ? 'text-primary-500' : 'text-gray-400'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 0 1-.88-7.903A5 5 0 1 1 15.9 6L16 6a5 5 0 0 1 1 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
              </svg>
              <p class="mb-1 transition-colors" :class="isDragging ? 'text-primary-600 dark:text-primary-400 font-medium' : 'text-gray-600 dark:text-gray-300'">
                {{ isDragging ? '松开以开始上传' : '上传 Excel 文件生成报表' }}
              </p>
              <p class="text-sm text-gray-400">支持 .xlsx, .xls, .csv 格式</p>
            </template>
          </div>
          <input
            ref="fileInput"
            type="file"
            @change="handleFileChange"
            accept=".xlsx,.xls,.csv"
            class="hidden"
          />
        </div>
      </div>

      <!-- 消息列表 -->
      <div v-else class="max-w-4xl mx-auto space-y-6">
        <div
          v-for="message in messages"
          :key="message.id"
          class="flex gap-4 animate-slide-in"
          :class="{ 'flex-row-reverse': message.role === 'user' }"
        >
          <!-- 头像 -->
          <div
            class="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center"
            :class="message.role === 'user' ? 'bg-primary-500' : 'bg-gray-200 dark:bg-slate-700'"
          >
            <svg v-if="message.role === 'user'" class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0zM12 14a7 7 0 0 0-7 7h14a7 7 0 0 0-7-7z"/>
            </svg>
            <svg v-else class="w-6 h-6 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 1 1 7.072 0l-.548.547A3.374 3.374 0 0 0 14 18.469V19a2 2 0 1 1-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
            </svg>
          </div>

          <!-- 消息内容 -->
          <div class="max-w-[75%] min-w-[120px]">
            <div
              class="rounded-2xl px-4 py-3 overflow-hidden"
              :class="message.role === 'user' 
                ? 'bg-gradient-to-br from-primary-500 to-primary-600 text-white rounded-tr-sm shadow-sm shadow-primary-200 dark:shadow-primary-900/30' 
                : 'bg-white dark:bg-slate-800 text-gray-800 dark:text-white border border-gray-100 dark:border-slate-700/70 rounded-tl-sm shadow-sm'"
            >
              <MarkdownRenderer v-if="message.content && message.role !== 'user'" :content="message.content" />
              <p v-else-if="message.content" class="whitespace-pre-wrap">{{ message.content }}</p>
              
              <!-- 进度条 -->
              <div v-if="message.progress" class="mt-4">
                <div class="flex justify-between text-sm mb-2">
                  <span>{{ message.progress.message }}</span>
                  <span>{{ message.progress.step }}/{{ message.progress.total }}</span>
                </div>
                <div class="w-full bg-gray-100 dark:bg-slate-700 rounded-full h-2 overflow-hidden">
                  <div
                    class="h-full rounded-full bg-gradient-to-r from-primary-500 to-primary-400 transition-all duration-500 ease-out"
                    :style="{ width: `${(message.progress.step / message.progress.total) * 100}%` }"
                  ></div>
                </div>
              </div>
              
              <!-- 文件附件 -->
              <div v-if="message.attachments && message.attachments.length > 0" class="mt-3 space-y-2">
                <div
                  v-for="file in message.attachments"
                  :key="file.id"
                  class="flex items-center gap-3 bg-gray-50 dark:bg-slate-700 rounded-lg p-3"
                >
                  <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5.586a1 1 0 0 1 .707.293l5.414 5.414a1 1 0 0 1 .293.707V19a2 2 0 0 1-2 2z"/>
                  </svg>
                  <div class="flex-1 min-w-0">
                    <p class="font-medium text-gray-700 dark:text-gray-300 truncate">{{ file.name }}</p>
                    <p class="text-sm text-gray-400">{{ formatFileSize(file.size) }}</p>
                  </div>
                </div>
              </div>
              
              <!-- 生成的图片 -->
              <div v-if="message.imageUrl" class="mt-4">
                <img
                  :src="message.imageUrl"
                  alt="Generated Report"
                  class="rounded-lg max-w-full shadow-lg cursor-pointer transition-opacity hover:opacity-90"
                  @click="previewImageUrl = message.imageUrl!"
                />
                <div class="mt-2 flex gap-2">
                  <button
                    @click="downloadImage(message.imageUrl!, message.content)"
                    class="inline-flex items-center gap-1.5 text-xs font-medium text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 bg-primary-50 dark:bg-primary-900/20 px-3 py-1.5 rounded-lg hover:bg-primary-100 dark:hover:bg-primary-900/40 transition-all"
                  >
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                    </svg>
                    下载图片
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部输入区域 -->
    <div class="border-t border-gray-100 dark:border-slate-700/50 bg-white dark:bg-slate-800 px-4 py-3">
      <div class="max-w-4xl mx-auto space-y-3">
        <!-- 已上传的文件 -->
        <div v-if="currentFile" class="flex items-center gap-3 bg-gray-50 dark:bg-slate-700/50 border border-gray-100 dark:border-slate-700 rounded-xl p-3">
          <div class="w-9 h-9 bg-primary-100 dark:bg-primary-900/30 rounded-lg flex items-center justify-center">
            <svg class="w-5 h-5 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5.586a1 1 0 0 1 .707.293l5.414 5.414a1 1 0 0 1 .293.707V19a2 2 0 0 1-2 2z"/>
            </svg>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-gray-700 dark:text-gray-300 truncate">{{ currentFile.fileName }}</p>
            <p class="text-xs text-gray-400">{{ currentFile.sheets.length }} 个工作簿</p>
          </div>
          <button @click="removeFile" class="p-1.5 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition-all">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>

        <!-- 输入框 -->
        <div class="flex gap-2">
          <div class="flex-1 relative">
            <input
              v-model="inputMessage"
              @keyup.enter="handleSend"
              :placeholder="currentFile ? '输入你的分析需求...' : '输入消息，或上传 Excel 文件分析...'"
              class="w-full bg-gray-50 dark:bg-slate-700/50 border border-gray-200 dark:border-slate-600 rounded-xl px-4 py-3 pr-12 text-sm text-gray-800 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500/40 focus:border-primary-500 transition-all shadow-sm"
              :disabled="loading"
            />
            <button
              @click="triggerUpload"
              class="absolute right-3 top-1/2 -translate-y-1/2 p-1.5 rounded-lg text-gray-400 hover:text-primary-500 hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-all"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 0 1-.88-7.903A5 5 0 1 1 15.9 6L16 6a5 5 0 0 1 1 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
              </svg>
            </button>
            <input
              ref="fileInput"
              type="file"
              @change="handleFileChange"
              accept=".xlsx,.xls,.csv"
              class="hidden"
            />
          </div>
          <button
            @click="handleSend"
            :disabled="!inputMessage.trim() || loading"
            class="px-6 py-3 bg-primary-500 hover:bg-primary-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-white rounded-xl font-medium transition-all duration-200 hover:-translate-y-0.5 hover:shadow-lg flex items-center gap-2"
          >
            <svg v-if="loading" class="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
            </svg>
            <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
            </svg>
            {{ loading ? '生成中...' : '发送' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 图片预览 -->
    <ImagePreview
      :url="previewImageUrl || ''"
      :visible="!!previewImageUrl"
      @close="previewImageUrl = null"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { apiService } from '@/services/api'
import { t } from '@/i18n'
import type { Message, FileAttachment, UploadResponse } from '@/types'
import MarkdownRenderer from '@/components/MarkdownRenderer.vue'
import ImagePreview from '@/components/ImagePreview.vue'

const appStore = useAppStore()
const tt = (key: string) => t(key, appStore.locale)

const fileInput = ref<HTMLInputElement | null>(null)
const inputMessage = ref('')
const uploadedFileData = ref<UploadResponse | null>(null)
const currentTaskId = ref<string | null>(null)
const eventSource = ref<EventSource | null>(null)
const previewImageUrl = ref<string | null>(null)
const messageContainer = ref<HTMLElement | null>(null)
const isDragging = ref(false)
const isUploading = ref(false)

const route = useRoute()

const messages = computed(() => appStore.messages)
const currentFile = computed(() => appStore.currentFile)
const loading = computed(() => appStore.loading)

// ── 加载历史记录 ──
async function loadHistory(type: string, id: string) {
  appStore.clearMessages()
  try {
    if (type === 'chat') {
      const res: any = await apiService.getChatHistoryDetail(id)
      const d = res as any
      appStore.addMessage({ id: 'hist-user', role: 'user', content: d.userMessage || '', timestamp: Date.now() })
      appStore.addMessage({ id: 'hist-ai', role: 'assistant', content: d.aiReply || '', timestamp: Date.now() + 1 })
    } else {
      const res: any = await apiService.getHistoryDetail(id)
      const d = res as any
      appStore.addMessage({ id: 'hist-user', role: 'user', content: d.userPrompt || '', timestamp: Date.now() })
      if (d.imageUrl) {
        appStore.addMessage({
          id: 'hist-ai',
          role: 'assistant',
          content: d.generatedPrompt || '报表已生成',
          imageUrl: d.imageUrl,
          timestamp: Date.now() + 1,
        })
      }
    }
  } catch (e) {
    console.error('加载历史记录失败:', e)
  }
}

onMounted(() => {
  const historyId = route.query.historyId as string
  const historyType = (route.query.historyType as string) || 'chat'
  if (historyId) {
    loadHistory(historyType, historyId)
  }
})

function triggerUpload() {
  fileInput.value?.click()
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function handleDrop(event: DragEvent) {
  const files = event.dataTransfer?.files
  if (files && files.length > 0) {
    handleFile(files[0])
  }
}

function handleFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  const files = target.files
  if (files && files.length > 0) {
    handleFile(files[0])
  }
}

async function handleFile(file: File) {
  isDragging.value = false
  isUploading.value = true

  // 上传文件到后端
  try {
    const uploadResponse = await apiService.uploadFile(file)
    isUploading.value = false

    const attachment: FileAttachment = {
      id: Date.now().toString(),
      name: file.name,
      type: file.name.endsWith('.csv') ? 'csv' : file.name.endsWith('.xls') ? 'xls' : 'xlsx',
      size: file.size
    }

    const message: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: `上传了文件 ${file.name}`,
      timestamp: Date.now(),
      attachments: [attachment]
    }
    appStore.addMessage(message)
    uploadedFileData.value = uploadResponse
    
    // 设置当前文件
    const mockFile = {
      fileId: uploadResponse.fileId,
      fileName: uploadResponse.fileName,
      sheets: uploadResponse.sheets.map(sheet => ({
        name: sheet.name,
        headers: [],
        rows: [],
        summary: {
          numericColumns: [],
          categoricalColumns: [],
          dateColumns: []
        }
      })),
      metadata: {
        totalRows: uploadResponse.metadata.totalRows,
        totalCols: uploadResponse.metadata.totalCols,
        sheetCount: uploadResponse.sheets.length
      }
    }
    appStore.setCurrentFile(mockFile)

    // ── 上传后自动触发大模型分析 + 图片生成 ──
    await generateReport(uploadResponse.fileId, '这是上传的完整数据，包含全部行和列。请全面分析所有数据的内容、结构、趋势、分布和统计特征，然后生成对应的数据可视化报表。')
    
  } catch (error) {
    console.error('Upload failed:', error)
    isUploading.value = false
    const errorMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: '文件上传失败，请重试',
      timestamp: Date.now()
    }
    appStore.addMessage(errorMessage)
  }
}

function removeFile() {
  appStore.setCurrentFile(null)
  uploadedFileData.value = null
}

function downloadImage(url: string, filename: string) {
  const a = document.createElement('a')
  a.href = url
  a.download = filename || 'report.png'
  a.click()
}

async function handleSend() {
  const text = inputMessage.value.trim()
  if (!text || loading.value) return

  // 添加用户消息
  const userMessage: Message = {
    id: Date.now().toString(),
    role: 'user',
    content: text,
    timestamp: Date.now()
  }
  appStore.addMessage(userMessage)
  inputMessage.value = ''

  // 有文件 → 生成报表模式，无文件 → 聊天模式
  if (currentFile.value && uploadedFileData.value) {
    await generateReport(uploadedFileData.value.fileId, text)
  } else {
    await sendChat(text)
  }
}

async function generateReport(fileId: string, userPrompt: string) {
  appStore.setLoading(true)
  
  try {
    // 添加思考中消息
    const thinkingMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: '正在创建生成任务...',
      timestamp: Date.now(),
      progress: {
        step: 0,
        total: 4,
        message: '准备中...'
      }
    }
    appStore.addMessage(thinkingMessage)
    
    // 1. 创建任务
    const generateResponse = await apiService.generateReport({
      fileId: fileId,
      userPrompt: userPrompt
    })
    
    currentTaskId.value = generateResponse.taskId
    
    // 连接 SSE
    connectSSE(generateResponse.taskId, thinkingMessage.id)
    
    // 2. 执行生成任务
    await apiService.executeTask(generateResponse.taskId)
    
  } catch (error) {
    console.error('Generate failed:', error)
    const errorMessage: Message = {
      id: (Date.now() + 2).toString(),
      role: 'assistant',
      content: '生成报表时出错，请重试',
      timestamp: Date.now()
    }
    appStore.addMessage(errorMessage)
    appStore.setLoading(false)
    closeSSE()
  }
}

async function sendChat(text: string) {
  appStore.setLoading(true)

  // 添加思考中消息
  const thinkingMessage: Message = {
    id: (Date.now() + 1).toString(),
    role: 'assistant',
    content: '思考中...',
    timestamp: Date.now(),
  }
  appStore.addMessage(thinkingMessage)

  try {
    const res: any = await apiService.chat(text)
    // 更新思考中消息为实际回复
    thinkingMessage.content = res.reply || '收到你的消息了！'
    const idx = appStore.messages.findIndex(m => m.id === thinkingMessage.id)
    if (idx > -1) {
      appStore.messages[idx] = { ...thinkingMessage }
    }
  } catch (error) {
    console.error('Chat failed:', error)
    thinkingMessage.content = '聊天服务暂时不可用，请稍后再试'
    const idx = appStore.messages.findIndex(m => m.id === thinkingMessage.id)
    if (idx > -1) {
      appStore.messages[idx] = { ...thinkingMessage }
    }
  } finally {
    appStore.setLoading(false)
  }
}

function connectSSE(taskId: string, messageId: string) {
  // 确保之前的连接关闭
  closeSSE()
  
  // 注意：不需要加 /v1 前缀，因为 vite 代理会自动添加
  const url = `/api/sse/${taskId}`
  eventSource.value = new EventSource(url)
  
  eventSource.value.onopen = () => {
    console.log('SSE 连接已建立')
  }
  
  eventSource.value.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      handleSSEEvent(data, messageId)
    } catch (e) {
      console.error('解析 SSE 数据失败:', e)
    }
  }
  
  eventSource.value.onerror = (error) => {
    console.error('SSE 连接错误:', error)
    closeSSE()
  }
}

function handleSSEEvent(event: any, messageId: string) {
  const index = appStore.messages.findIndex(m => m.id === messageId)
  if (index === -1) return
  
  const message = { ...appStore.messages[index] }
  
  switch (event.type) {
    case 'progress':
      message.content = event.data.message
      message.progress = {
        step: event.data.step,
        total: event.data.total,
        message: event.data.message
      }
      appStore.messages[index] = message
      break
      
    case 'prompt_generated':
      // 可以保存生成的提示词
      break
      
    case 'complete':
      message.content = `已根据你的需求分析完成！${event.data.generated_prompt ? '\n\n' + event.data.generated_prompt : ''}`
      message.imageUrl = event.data.image_url || 'https://picsum.photos/800/500?random=' + Date.now()
      message.progress = undefined
      appStore.messages[index] = message
      appStore.setLoading(false)
      closeSSE()
      break
      
    case 'error':
      message.content = `生成失败: ${event.data.message}`
      message.progress = undefined
      appStore.messages[index] = message
      appStore.setLoading(false)
      closeSSE()
      break
  }
}

function closeSSE() {
  if (eventSource.value) {
    eventSource.value.close()
    eventSource.value = null
  }
}

function scrollToBottom() {
  nextTick(() => {
    if (messageContainer.value) {
      messageContainer.value.scrollTop = messageContainer.value.scrollHeight
    }
  })
}

// 监听消息变化，自动滚动到底部
watch(() => appStore.messages.length, () => {
  scrollToBottom()
})

// 深度监听消息属性变化（进度更新、图片URL、内容更新）
watch(() => appStore.messages, () => {
  scrollToBottom()
}, { deep: true })

onBeforeUnmount(() => {
  closeSSE()
})
</script>
