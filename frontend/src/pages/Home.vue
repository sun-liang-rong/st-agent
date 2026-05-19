<template>
  <div class="h-full flex flex-col bg-gray-50 dark:bg-slate-900">
    <!-- 消息列表 -->
    <div ref="messageContainer" class="flex-1 overflow-y-auto p-6 space-y-6">
      <!-- 空状态：无消息、无预览 -->
      <div v-if="messages.length === 0 && !previewData" class="flex flex-col items-center justify-center h-full text-center px-6 animate-slide-in">
        <div class="relative mb-6">
          <div class="w-20 h-20 bg-gradient-to-br from-primary-100 to-primary-200 dark:from-primary-900/40 dark:to-primary-800/30 rounded-2xl flex items-center justify-center shadow-inner">
            <svg class="w-10 h-10 text-primary-500 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 1 1 7.072 0l-.548.547A3.374 3.374 0 0 0 14 18.469V19a2 2 0 1 1-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
            </svg>
          </div>
          <!-- 装饰小圆点 -->
          <div class="absolute -top-1 -right-1 w-6 h-6 bg-amber-100 dark:bg-amber-900/30 rounded-full flex items-center justify-center animate-pulse">
            <svg class="w-3 h-3 text-amber-500" fill="currentColor" viewBox="0 0 20 20">
              <path d="M11 3a1 1 0 10-2 0v1a1 1 0 102 0V3zM15.657 5.757a1 1 0 00-1.414-1.414l-.707.707a1 1 0 001.414 1.414l.707-.707zM18 10a1 1 0 01-1 1h-1a1 1 0 110-2h1a1 1 0 011 1zM5.05 6.464A1 1 0 106.464 5.05l-.707-.707a1 1 0 00-1.414 1.414l.707.707zM5 10a1 1 0 01-1 1H3a1 1 0 110-2h1a1 1 0 011 1zM8 16v-1h4v1a2 2 0 11-4 0zM12 14c.015-.34.208-.646.477-.859a4 4 0 10-4.954 0c.27.213.462.519.476.859h4.002z"/>
            </svg>
          </div>
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
            class="border-2 border-dashed rounded-xl p-12 transition-all duration-300 group"
            :class="[
              isDragging
                ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20 scale-[1.02] shadow-lg shadow-primary-200 dark:shadow-primary-900/30'
                : 'border-gray-300 dark:border-slate-600 hover:border-primary-500 dark:hover:border-primary-400 hover:bg-gray-50/50 dark:hover:bg-slate-800/30 hover:shadow-md',
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

      <!-- 数据预览 + 配置面板 -->
      <div v-else-if="previewData && messages.length === 0" class="flex-1 overflow-y-auto">
        <div class="max-w-4xl mx-auto py-6 px-6 space-y-6">
          <!-- 预览中加载 -->
          <div v-if="previewLoading" class="flex flex-col items-center justify-center py-20">
            <svg class="w-10 h-10 text-primary-500 animate-spin mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
            </svg>
            <p class="text-gray-500 dark:text-gray-400">正在加载数据预览...</p>
          </div>
          <!-- 预览 + 配置 -->
          <template v-else>
            <DataPreview
              :preview="previewData"
              @update:selectedColumns="selectedColumns = $event"
            />
            <ReportConfig
              :currentFile="currentFile"
              :selectedColumns="selectedColumns"
              :defaultPrompt="aiSuggestion"
              @generate="generateFromConfig"
            />
          </template>
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
          <div class="max-w-[75%] min-w-[120px] group/message">
            <div
              class="rounded-2xl px-4 py-3 overflow-hidden transition-all duration-200"
              :class="message.role === 'user' 
                ? 'bg-gradient-to-br from-primary-500 to-primary-600 text-white rounded-tr-sm shadow-sm shadow-primary-200 dark:shadow-primary-900/30' 
                : 'bg-white dark:bg-slate-800 text-gray-800 dark:text-white border border-gray-100 dark:border-slate-700/70 rounded-tl-sm shadow-sm hover:shadow-md dark:hover:border-slate-600'"
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
                  class="rounded-lg max-w-full shadow-lg"
                />
              </div>

              <div v-if="message.dashboardSpec && message.phase === 'complete'" class="mt-4">
                <DashboardRenderer :spec="message.dashboardSpec" />
              </div>

              <!-- 提示词确认（两阶段模式） -->
              <div v-if="message.phase === 'prompt' && message.dashboardSpec" class="mt-3 space-y-3">
                <div class="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-700 rounded-lg p-3">
                  <p class="text-sm font-medium text-gray-800 dark:text-gray-200">📊 看板方案已生成</p>
                  <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">AI 生成了以下看板配置，你可以编辑后确认渲染</p>
                </div>
                <DashboardRenderer :spec="message.dashboardSpec" />
                <details class="bg-gray-50 dark:bg-slate-700/30 rounded-lg border border-gray-200 dark:border-slate-600">
                  <summary class="px-4 py-2 text-sm font-medium text-gray-600 dark:text-gray-300 cursor-pointer hover:bg-gray-100 dark:hover:bg-slate-700/50 rounded-lg transition-colors">编辑 JSON 配置</summary>
                  <div class="px-4 pb-4">
                    <textarea :value="JSON.stringify(editingSpec, null, 2)" @input="onSpecEdit($event)" rows="12" class="w-full px-3 py-2 bg-white dark:bg-slate-700 border border-gray-200 dark:border-slate-600 rounded-lg text-xs text-gray-800 dark:text-white font-mono focus:outline-none focus:ring-2 focus:ring-primary-500/40 transition-all resize-y" placeholder="看板 JSON 配置..." :disabled="isPhase2Loading"></textarea>
                  </div>
                </details>
                <div class="flex gap-2">
                  <button @click="confirmGenerate(message)" :disabled="isPhase2Loading" class="flex-1 py-2.5 px-4 bg-gradient-to-r from-primary-600 to-primary-500 hover:from-primary-700 hover:to-primary-600 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-xl text-sm font-medium shadow-lg shadow-primary-200 dark:shadow-primary-900/30 transition-all duration-200 flex items-center justify-center gap-2">
                    <svg v-if="isPhase2Loading" class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
                    {{ isPhase2Loading ? '渲染中...' : '✅ 确认渲染看板' }}
                  </button>
                  <button @click="cancelAndRetry(message)" :disabled="isPhase2Loading" class="py-2.5 px-4 bg-gray-100 dark:bg-slate-700 text-gray-600 dark:text-gray-300 rounded-xl text-sm font-medium hover:bg-gray-200 dark:hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all">🔄 重新分析</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部输入区域（渐变分隔线） -->
    <div class="relative bg-white dark:bg-slate-800 px-4 pt-1">
      <!-- 渐变分隔线 -->
      <div class="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-gray-200 dark:via-slate-600 to-transparent"></div>
      <div class="max-w-4xl mx-auto py-3 space-y-3">
        <!-- 已上传的文件 -->
        <div v-if="currentFile" class="flex items-center gap-3 bg-gradient-to-r from-primary-50 to-primary-50/30 dark:from-primary-900/15 dark:to-slate-800 border border-primary-100 dark:border-primary-900/30 rounded-xl p-3 group/chip transition-all duration-200 hover:shadow-sm">
          <div class="w-9 h-9 bg-primary-100 dark:bg-primary-900/30 rounded-lg flex items-center justify-center shrink-0">
            <svg class="w-5 h-5 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5.586a1 1 0 0 1 .707.293l5.414 5.414a1 1 0 0 1 .293.707V19a2 2 0 0 1-2 2z"/>
            </svg>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-gray-700 dark:text-gray-300 truncate">{{ currentFile.fileName }}</p>
            <p class="text-xs text-gray-400">{{ currentFile.sheets.length }} 个工作簿 · {{ currentFile.metadata.totalRows }} 行数据</p>
          </div>
          <button @click="removeFile" class="p-1.5 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition-all opacity-0 group-hover/chip:opacity-100">
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
              class="w-full bg-gray-50 dark:bg-slate-700/50 border border-gray-200 dark:border-slate-600 rounded-xl px-4 py-3 pr-12 text-sm text-gray-800 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 focus:bg-white dark:focus:bg-slate-700 transition-all shadow-sm"
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
            class="px-6 py-3 bg-primary-500 hover:bg-primary-600 active:scale-95 active:bg-primary-700 disabled:bg-gray-300 disabled:active:scale-100 disabled:cursor-not-allowed text-white rounded-xl font-medium transition-all duration-200 hover:-translate-y-0.5 hover:shadow-lg disabled:hover:translate-y-0 disabled:hover:shadow-none flex items-center gap-2"
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

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { apiService } from '@/services/api'
import { t } from '@/i18n'
import type { Message, FileAttachment, UploadResponse, PreviewResponse, ChartType } from '@/types'
import MarkdownRenderer from '@/components/MarkdownRenderer.vue'
import DataPreview from '@/components/DataPreview.vue'
import ReportConfig from '@/components/ReportConfig.vue'
import DashboardRenderer from '@/components/DashboardRenderer.vue'
import type { DashboardSpec } from '@/types'

const appStore = useAppStore()
const tt = (key: string) => t(key, appStore.locale)

const fileInput = ref<HTMLInputElement | null>(null)
const inputMessage = ref('')
const uploadedFileData = ref<UploadResponse | null>(null)
const currentTaskId = ref<string | null>(null)
const eventSource = ref<EventSource | null>(null)
const messageContainer = ref<HTMLElement | null>(null)
const isDragging = ref(false)
const isUploading = ref(false)

// ── 数据预览 & 用户配置状态 ──
const previewData = ref<PreviewResponse | null>(null)
const previewLoading = ref(false)
const selectedColumns = ref<string[]>([])

// ── AI 建议提示词 ──
const aiSuggestion = ref<string>('')

// ── 两阶段模式状态 ──
const editingPrompts = ref<Record<string, string>>({})
const isPhase2Loading = ref(false)
const lastChartType = ref<ChartType>('bar')
const editingSpec = ref<DashboardSpec | null>(null)

const route = useRoute()

const messages = computed(() => appStore.messages)
const currentFile = computed(() => appStore.currentFile)
const loading = computed(() => appStore.loading)

// ── 加载单条历史记录（兼容旧格式） ──
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
      if (d.dashboardSpec) {
        appStore.addMessage({
          id: 'hist-ai', role: 'assistant', content: '',
          dashboardSpec: d.dashboardSpec, phase: 'complete', timestamp: Date.now() + 1,
        })
      }
    }
  } catch (e) {
    console.error('加载历史记录失败:', e)
  }
}

// ── 加载多条历史记录（完整会话） ──
async function loadHistoryItems(items: { type: string; rawId: string }[]) {
  appStore.clearMessages()
  for (let i = 0; i < items.length; i++) {
    const item = items[i]
    const baseTime = Date.now() + i * 100 // 每批消息间隔 100ms 保证顺序
    try {
      if (item.type === 'chat') {
        const res: any = await apiService.getChatHistoryDetail(item.rawId)
        const d = res as any
        appStore.addMessage({
          id: `hist-chat-${item.rawId}-user`,
          role: 'user',
          content: d.userMessage || '',
          timestamp: baseTime,
        })
        appStore.addMessage({
          id: `hist-chat-${item.rawId}-ai`,
          role: 'assistant',
          content: d.aiReply || '',
          timestamp: baseTime + 1,
        })
      } else {
        const res: any = await apiService.getHistoryDetail(item.rawId)
        const d = res as any
        appStore.addMessage({
          id: `hist-report-${item.rawId}-user`,
          role: 'user',
          content: d.userPrompt || '',
          timestamp: baseTime,
        })
        if (d.dashboardSpec) {
          appStore.addMessage({
            id: `hist-report-${item.rawId}-ai`,
            role: 'assistant',
            content: '',
            dashboardSpec: d.dashboardSpec,
            phase: 'complete',
            timestamp: baseTime + 1,
          })
        }
      }
    } catch (e) {
      console.error(`加载历史记录失败 (${item.type}/${item.rawId}):`, e)
    }
  }
}

// ── 从路由 query 加载历史记录 ──
async function loadHistoryFromQuery(query: any) {
  const historyItems = query.historyItems as string
  if (historyItems) {
    try {
      const items: { type: string; rawId: string }[] = JSON.parse(decodeURIComponent(historyItems))
      await loadHistoryItems(items)
    } catch (e) {
      console.error('解析历史记录参数失败:', e)
    }
  } else {
    // 兼容旧格式：单条记录
    const historyId = query.historyId as string
    if (historyId) {
      const historyType = (query.historyType as string) || 'chat'
      await loadHistory(historyType, historyId)
    }
  }
}

onMounted(() => {
  loadHistoryFromQuery(route.query)
})

// 同路由 query 变化时重新加载（比如从历史页连续点击不同会话）
watch(() => route.query, (query) => {
  loadHistoryFromQuery(query)
}, { deep: true })

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
    const file = files[0]
    const allowedExts = ['.xlsx', '.xls', '.csv']
    const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase()
    if (!allowedExts.includes(ext)) return
    handleFile(file)
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

    // ── 拉取数据预览 + AI 建议（并行） ──
    previewLoading.value = true
    try {
      const [preview, suggestRes] = await Promise.all([
        apiService.getFilePreview(uploadResponse.fileId),
        apiService.suggestPrompt(uploadResponse.fileId).catch(e => {
          console.error('获取建议提示词失败:', e)
          return { suggestion: '' }
        }),
      ])
      previewData.value = preview
      selectedColumns.value = [...preview.columnNames]
      aiSuggestion.value = suggestRes.suggestion
    } catch (e) {
      console.error('获取数据预览失败:', e)
    } finally {
      previewLoading.value = false
    }
    
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
  appStore.resetConversation()
  uploadedFileData.value = null
  previewData.value = null
  selectedColumns.value = []
}

// ── 从配置面板触发生成 ──
async function generateFromConfig(config: {
  userPrompt: string
  selectedColumns: string[]
  chartType: ChartType
  chartTitle: string
}) {
  if (!uploadedFileData.value) return

  lastChartType.value = config.chartType

  // 隐藏预览配置区
  previewData.value = null

  // 添加用户消息
  const userMessage: Message = {
    id: Date.now().toString(),
    role: 'user',
    content: config.userPrompt,
    timestamp: Date.now()
  }
  appStore.addMessage(userMessage)

  // 调用阶段1：分析数据 + 生成提示词
  await generatePhase1(
    uploadedFileData.value.fileId,
    config.userPrompt,
    config.selectedColumns,
    config.chartType,
    config.chartTitle,
  )
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
    if (previewData.value) {
      // 有预览数据时，带上当前的列选择
      await generateFromConfig({
        userPrompt: text,
        selectedColumns: selectedColumns.value,
        chartType: lastChartType.value,
        chartTitle: '',
      })
    } else {
      await generatePhase1(uploadedFileData.value.fileId, text)
    }
  } else {
    await sendChat(text)
  }
}

async function generatePhase1(
  fileId: string,
  userPrompt: string,
  selectedColumns: string[] = [],
  chartType: string = 'bar',
  chartTitle: string = '',
) {
  appStore.setLoading(true)
  try {
    const thinkingMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: '正在分析数据...',
      timestamp: Date.now(),
      progress: { step: 0, total: 3, message: '准备中...' }
    }
    appStore.addMessage(thinkingMessage)
    const generateResponse = await apiService.generateReport({
      fileId: fileId,
      userPrompt: userPrompt,
      selectedColumns: selectedColumns.length > 0 ? selectedColumns : undefined,
      chartType: chartType,
      chartTitle: chartTitle || undefined,
    } as any)
    currentTaskId.value = generateResponse.taskId
    const dashboardSpec = generateResponse.dashboardSpec
    connectSSE(generateResponse.taskId, thinkingMessage.id)
    const idx = appStore.messages.findIndex(m => m.id === thinkingMessage.id)
    if (idx > -1 && dashboardSpec) {
      appStore.messages[idx] = {
        ...appStore.messages[idx],
        content: '',
        progress: undefined,
        phase: 'prompt',
        dashboardSpec: dashboardSpec,
      }
      editingSpec.value = dashboardSpec
    }
    appStore.setLoading(false)
  } catch (error) {
    console.error('生成失败:', error)
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


async function confirmGenerate(message: Message) {
  if (!editingSpec.value || !currentTaskId.value) return
  isPhase2Loading.value = true
  appStore.setLoading(true)
  try {
    const idx = appStore.messages.findIndex(m => m.id === message.id)
    if (idx > -1) {
      appStore.messages[idx] = {
        ...appStore.messages[idx],
        content: '',
        phase: 'complete',
        dashboardSpec: editingSpec.value,
        progress: undefined,
      }
    }
    await apiService.confirmDashboard(currentTaskId.value, editingSpec.value)
  } catch (error) {
    console.error('保存失败:', error)
    const idx = appStore.messages.findIndex(m => m.id === message.id)
    if (idx > -1) {
      appStore.messages[idx] = {
        ...appStore.messages[idx],
        content: '保存失败，请重试',
        progress: undefined,
      }
    }
  } finally {
    isPhase2Loading.value = false
    appStore.setLoading(false)
    closeSSE()
  }
}

function onSpecEdit(event: Event) {
  const target = event.target as HTMLTextAreaElement
  try {
    const parsed = JSON.parse(target.value)
    editingSpec.value = parsed
    const msg = appStore.messages.find(m => m.phase === 'prompt' && m.dashboardSpec)
    if (msg) {
      msg.dashboardSpec = parsed
    }
  } catch {
    // JSON 不合法，不更新
  }
}

function cancelAndRetry(message: Message) {
  const idx = appStore.messages.findIndex(m => m.id === message.id)
  if (idx > -1) {
    appStore.messages.splice(idx, 1)
  }
  editingSpec.value = null
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
