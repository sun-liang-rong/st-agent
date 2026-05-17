import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UserSettings, Message, ParsedExcel } from '@/types'

export const useAppStore = defineStore('app', () => {
  // 状态
  const locale = ref<'zh-CN' | 'en'>('zh-CN')
  const theme = ref<'light' | 'dark'>('light')
  const settings = ref<UserSettings>({
    theme: 'light',
    defaultPromptModel: 'shangtang-model-a',
    defaultImageModel: 'shangtang-model-b',
    apiKeys: {}
  })
  const currentFile = ref<ParsedExcel | null>(null)
  const messages = ref<Message[]>([])
  const currentTaskId = ref<string | null>(null)
  const loading = ref(false)
  const sideBarOpen = ref(true)

  // 计算属性
  const isDark = computed(() => theme.value === 'dark')

  // 方法
  function setLocale(l: 'zh-CN' | 'en') {
    locale.value = l
    localStorage.setItem('appLocale', l)
  }

  function toggleTheme() {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
    settings.value.theme = theme.value
    updateSettings()
  }

  function updateSettings(newSettings?: Partial<UserSettings>) {
    if (newSettings) {
      Object.assign(settings.value, newSettings)
    }
    localStorage.setItem('userSettings', JSON.stringify(settings.value))
  }

  function loadSettings() {
    // 读取语言
    const savedLocale = localStorage.getItem('appLocale')
    if (savedLocale === 'en' || savedLocale === 'zh-CN') {
      locale.value = savedLocale
    }
    // 读取其他设置
    const saved = localStorage.getItem('userSettings')
    if (saved) {
      try {
        const parsed = JSON.parse(saved)
        Object.assign(settings.value, parsed)
        theme.value = parsed.theme || 'light'
      } catch (e) {
        console.error('Failed to parse settings', e)
      }
    }
  }

  function addMessage(message: Message) {
    messages.value.push(message)
  }

  function clearMessages() {
    messages.value = []
    currentFile.value = null
    currentTaskId.value = null
  }

  function setCurrentFile(file: ParsedExcel | null) {
    currentFile.value = file
  }

  function setTaskId(taskId: string | null) {
    currentTaskId.value = taskId
  }

  function setLoading(state: boolean) {
    loading.value = state
  }

  function toggleSideBar() {
    sideBarOpen.value = !sideBarOpen.value
  }

  return {
    locale,
    theme,
    settings,
    currentFile,
    messages,
    currentTaskId,
    loading,
    sideBarOpen,
    isDark,
    toggleTheme,
    setLocale,
    updateSettings,
    loadSettings,
    addMessage,
    clearMessages,
    setCurrentFile,
    setTaskId,
    setLoading,
    toggleSideBar
  }
})
