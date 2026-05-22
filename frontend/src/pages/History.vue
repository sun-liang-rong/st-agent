<template>
  <div class="h-full bg-gray-50 dark:bg-slate-900 overflow-y-auto p-6">
    <div class="max-w-4xl mx-auto">
      <h1 class="text-2xl font-bold text-gray-800 dark:text-white mb-6">{{ tt('history.title') }}</h1>

      <!-- 骨架屏加载 -->
      <div v-if="loading" class="space-y-3">
        <div v-for="i in 5" :key="i" class="bg-white dark:bg-slate-800 rounded-xl p-5 shadow-sm border border-gray-50 dark:border-slate-700/30 animate-pulse">
          <div class="flex items-start justify-between gap-3">
            <div class="flex-1 space-y-3">
              <div class="h-5 bg-gray-200 dark:bg-slate-700 rounded-lg w-3/5 skeleton-shimmer"></div>
              <div class="h-4 bg-gray-200 dark:bg-slate-700 rounded-lg w-full skeleton-shimmer"></div>
              <div class="h-4 bg-gray-200 dark:bg-slate-700 rounded-lg w-2/3 skeleton-shimmer"></div>
              <div class="flex gap-2">
                <div class="h-3 bg-gray-200 dark:bg-slate-700 rounded w-24 skeleton-shimmer"></div>
                <div class="h-3 bg-gray-200 dark:bg-slate-700 rounded w-16 skeleton-shimmer"></div>
              </div>
            </div>
            <div class="w-8 h-8 bg-gray-200 dark:bg-slate-700 rounded-lg skeleton-shimmer flex-shrink-0"></div>
          </div>
        </div>
      </div>

      <div v-if="!loading && groups.length === 0" class="flex flex-col items-center justify-center py-20 text-center animate-slide-in">
        <!-- 空状态插图 -->
        <div class="relative mb-8">
          <svg class="w-32 h-32 text-gray-200 dark:text-slate-700" viewBox="0 0 120 120" fill="none">
            <circle cx="60" cy="60" r="50" stroke="currentColor" stroke-width="2" stroke-dasharray="4 4" opacity="0.3"/>
            <circle cx="60" cy="60" r="35" stroke="currentColor" stroke-width="1.5" stroke-dasharray="3 3" opacity="0.2"/>
            <!-- 时钟指针 -->
            <path d="M60 35V60L75 72" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" opacity="0.5"/>
            <circle cx="60" cy="60" r="4" fill="currentColor" opacity="0.4"/>
          </svg>
          <div class="absolute -top-1 -right-1 w-10 h-10 bg-primary-100 dark:bg-primary-900/30 rounded-full flex items-center justify-center">
            <svg class="w-5 h-5 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
            </svg>
          </div>
        </div>
        <h2 class="text-xl font-semibold text-gray-700 dark:text-gray-200 mb-2">暂无历史记录</h2>
        <p class="text-gray-400 dark:text-gray-500 max-w-xs">{{ tt('history.empty') }}</p>
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="group in groups"
          :key="group.id"
          class="bg-white dark:bg-slate-800 rounded-xl p-5 shadow-sm hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200 cursor-pointer border border-gray-50 dark:border-slate-700/30"
          @click="openGroup(group)"
        >
          <div class="flex items-start justify-between gap-3">
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2">
                <span v-if="group.sessionType === 'image'" class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-amber-100 dark:bg-amber-900/30 text-xs text-amber-700 dark:text-amber-300">🎨 图片生成</span>
                <span v-else class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-blue-100 dark:bg-blue-900/30 text-xs text-blue-700 dark:text-blue-300">💬 对话</span>
                <h3 class="text-base font-semibold text-gray-800 dark:text-white truncate">
                  {{ group.title }}
                </h3>
              </div>
              <p class="text-sm text-gray-500 dark:text-gray-400 mt-1 line-clamp-2">
                {{ group.summary }}
              </p>
              <div class="flex items-center gap-2 mt-2">
                <span class="text-xs text-gray-400">{{ formatDate(group.createdAt) }}</span>
                <span class="text-xs text-gray-300 dark:text-gray-600">·</span>
                <span class="text-xs text-gray-400">{{ group.count }} {{ tt('history.interactions') }}</span>
              </div>
            </div>
            <button @click.stop="deleteGroup(group)" class="p-1.5 rounded-lg text-gray-500 dark:text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition-all flex-shrink-0 border border-gray-200 dark:border-gray-600 hover:border-red-300 dark:hover:border-red-700" title="删除">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <ConfirmDialog ref="confirmRef" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { apiService } from '@/services/api'
import { useAppStore } from '@/stores/app'
import { t } from '@/i18n'
import ConfirmDialog from '@/components/ConfirmDialog.vue'

const router = useRouter()
const appStore = useAppStore()
const tt = (key: string) => t(key, appStore.locale)
const confirmRef = ref<InstanceType<typeof ConfirmDialog> | null>(null)

interface RawItem {
  id: string        // "report-3" or "chat-5"
  type: 'report' | 'chat'
  title: string
  summary: string
  createdAt: string
  rawId: string     // real DB id
  contextId?: string // chat 记录的会话分组 ID
  sessionType?: string // chat 或 image
}

interface HistoryGroup {
  id: string
  title: string
  summary: string
  createdAt: string
  count: number
  items: RawItem[]
  sessionType: string // chat 或 image
}

const groups = ref<HistoryGroup[]>([])
const loading = ref(true)

const SESSION_GAP_MS = 5 * 60 * 1000 // 5 分钟

function formatDate(dateString: string): string {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('zh-CN', {
    year: 'numeric', month: 'long', day: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

// function parsePrefixedId(prefixed: string) {
//   const sep = prefixed.indexOf('-')
//   return { prefix: prefixed.slice(0, sep), rawId: prefixed.slice(sep + 1) }
// }

function openGroup(group: HistoryGroup) {
  const chatItem = group.items.find(item => item.type === 'chat' && item.contextId)
  if (chatItem && chatItem.contextId) {
    if (group.sessionType === 'image') {
      router.push({ path: '/image', query: { sessionId: chatItem.contextId } })
    } else {
      router.push({ path: '/app', query: { sessionId: chatItem.contextId } })
    }
    return
  }
  router.push({ path: '/app' })
}

async function deleteGroup(group: HistoryGroup) {
  if (!confirmRef.value) return
  const ok = await confirmRef.value.confirm({
    title: '确认删除',
    message: `删除「${group.title}」后无法恢复，包含 ${group.count} 条记录`,
    type: 'danger',
  })
  if (!ok) return
  const promises: Promise<any>[] = []
  const chatContextIds = new Set<string>()
  for (const item of group.items) {
    if (item.type === 'chat' && item.contextId) {
      chatContextIds.add(item.contextId)
    }
  }
  for (const contextId of chatContextIds) {
    promises.push(apiService.deleteChatHistory(contextId))
  }
  for (const item of group.items) {
    if (item.type === 'report') {
      promises.push(apiService.deleteHistory(item.rawId))
    }
  }
  Promise.all(promises).then(() => {
    groups.value = groups.value.filter(g => g.id !== group.id)
  }).catch(() => alert('删除失败'))
}

onMounted(async () => {
  loading.value = true
  try {
    const [reportRes, chatRes] = await Promise.all([
      apiService.getHistory(),
      apiService.getChatHistory(),
    ])

    const raw: RawItem[] = [
      ...(Array.isArray(reportRes) ? reportRes : ((reportRes as any).data || [])).map((r: any) => ({
        id: `report-${r.id}`,
        type: 'report' as const,
        title: r.fileName?.replace(/\.(xlsx|xls|csv)$/i, '') || '报表',
        summary: r.userPrompt || '',
        createdAt: r.createdAt,
        rawId: String(r.id),
      })),
      ...(Array.isArray(chatRes) ? chatRes : ((chatRes as any).data || [])).map((c: any) => ({
        id: `chat-${c.id}`,
        type: 'chat' as const,
        contextId: c.contextId,
        sessionType: c.sessionType || 'chat',
        title: c.title || c.userMessage?.slice(0, 30) + '...',
        summary: c.userMessage || '',
        createdAt: c.createdAt,
        rawId: String(c.id),
      })),
    ]

    // 按时间升序排列
    raw.sort((a, b) => new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime())

    // 先用 contextId 分组，没有 contextId 的按时间窗口（5分钟）分组
    const contextGroups = new Map<string, RawItem[]>()
    const timeGroupItems: RawItem[] = []

    for (const item of raw) {
      if (item.type === 'chat' && 'contextId' in item && item.contextId) {
        const key = item.contextId
        if (!contextGroups.has(key)) contextGroups.set(key, [])
        contextGroups.get(key)!.push(item)
      } else {
        timeGroupItems.push(item)
      }
    }

    const result: HistoryGroup[] = []

    // contextId 分组：每组作为一个会话
    for (const [, items] of contextGroups) {
      result.push(buildGroup(items))
    }

    // 时间窗口分组（无 contextId 的记录）
    timeGroupItems.sort((a, b) => new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime())
    let window: RawItem[] = []
    let windowStart = 0
    for (const item of timeGroupItems) {
      const t = new Date(item.createdAt).getTime()
      if (window.length === 0) {
        window = [item]
        windowStart = t
      } else if (t - windowStart <= SESSION_GAP_MS) {
        window.push(item)
      } else {
        if (window.length > 0) result.push(buildGroup(window))
        window = [item]
        windowStart = t
      }
    }
    if (window.length > 0) result.push(buildGroup(window))

    // 按时间倒序（最新的在前）
    result.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
    groups.value = result
  } catch (e) {
    console.error('获取历史记录失败:', e)
  } finally {
    loading.value = false
  }
})

function buildGroup(items: RawItem[]): HistoryGroup {
  const first = items[0]
  const last = items[items.length - 1]
  const sessionType = items.find(i => i.sessionType)?.sessionType || 'chat'
  return {
    id: `group-${first.rawId}`,
    title: first.title,
    summary: first.summary,
    createdAt: last.createdAt,
    count: items.length,
    items,
    sessionType,
  }
}
</script>
