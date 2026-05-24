import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UserSettings, Message, ParsedExcel } from '@/types'

export type ThemeMode = 'light' | 'dark' | 'system'

export const useAppStore = defineStore('app', () => {
  // 状态
  const locale = ref<'zh-CN' | 'en'>('zh-CN')
  const theme = ref<ThemeMode>('system')
  const settings = ref<UserSettings>({
    theme: 'system',
    fontSize: 'medium',
    codeFont: 'mono',
    messageDensity: 'comfortable',
    defaultPromptModel: 'shangtang-model-a',
    apiKeys: {}
  })
  const currentFile = ref<ParsedExcel | null>(null)
  const messages = ref<Message[]>([])
  const loading = ref(false)
  const sideBarOpen = ref(true)

  // 系统偏好检测
  const prefersDark = ref(
    window.matchMedia('(prefers-color-scheme: dark)').matches
  )

  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    prefersDark.value = e.matches
    if (theme.value === 'system') {
      applyTheme()
    }
  })

  // 计算属性
  const isDark = computed(() => {
    if (theme.value === 'system') return prefersDark.value
    return theme.value === 'dark'
  })

  const resolvedTheme = computed<'light' | 'dark'>(() => isDark.value ? 'dark' : 'light')

  // DOM 同步
  let initialized = false
  function applyTheme() {
    const root = document.documentElement
    const shouldAnimate = initialized
    // 首次不动画（FOUC 脚本已处理），后续切换加过渡
    if (shouldAnimate) {
      root.classList.add('theme-transition')
    }
    root.classList.toggle('dark', isDark.value)
    if (shouldAnimate) {
      const onEnd = () => {
        root.classList.remove('theme-transition')
        root.removeEventListener('transitionend', onEnd)
      }
      root.addEventListener('transitionend', onEnd)
      setTimeout(() => {
        root.classList.remove('theme-transition')
        root.removeEventListener('transitionend', onEnd)
      }, 350)
    }
    initialized = true
  }

  // 方法
  function setLocale(l: 'zh-CN' | 'en') {
    locale.value = l
    localStorage.setItem('appLocale', l)
  }

  function setTheme(t: ThemeMode) {
    theme.value = t
    settings.value.theme = t
    updateSettings()
    applyTheme()
  }

  function toggleTheme() {
    const order: ThemeMode[] = ['light', 'dark', 'system']
    const idx = order.indexOf(theme.value)
    theme.value = order[(idx + 1) % order.length]
    settings.value.theme = theme.value
    updateSettings()
    applyTheme()
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
        // 兼容旧值：如果存储的是 'light' 或 'dark'，直接使用；否则默认 'system'
        const savedTheme = parsed.theme
        if (savedTheme === 'light' || savedTheme === 'dark' || savedTheme === 'system') {
          theme.value = savedTheme
        } else {
          theme.value = 'system'
        }
      } catch (e) {
        console.error('Failed to parse settings', e)
      }
    }
    // 启动时同步 DOM
    applyTheme()
  }

  function addMessage(message: Message) {
    messages.value.push(message)
  }

  function clearMessages() {
    messages.value = []
  }

  function resetConversation() {
    messages.value = []
    currentFile.value = null
    loading.value = false
  }

  function setCurrentFile(file: ParsedExcel | null) {
    currentFile.value = file
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
    loading,
    sideBarOpen,
    isDark,
    resolvedTheme,
    prefersDark,
    toggleTheme,
    setTheme,
    setLocale,
    updateSettings,
    loadSettings,
    addMessage,
    clearMessages,
    resetConversation,
    setCurrentFile,
    setLoading,
    toggleSideBar
  }
})