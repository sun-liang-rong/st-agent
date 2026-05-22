<template>
  <div class="h-full bg-gray-50 dark:bg-slate-900 overflow-y-auto p-6">
    <div class="max-w-2xl mx-auto">
      <h1 class="text-2xl font-bold text-gray-800 dark:text-white mb-6">{{ tt('settings.title') }}</h1>

      <div class="space-y-6">
        <!-- 语言 -->
        <div class="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm">
          <h2 class="text-lg font-semibold text-gray-800 dark:text-white mb-4">{{ tt('settings.language') }}</h2>
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">{{ tt('settings.languageDesc') }}</p>
          <div class="flex gap-3">
            <button
              @click="switchLang('zh-CN')"
              class="flex-1 py-3 px-4 rounded-xl border-2 text-sm font-medium transition-all"
              :class="locale === 'zh-CN'
                ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                : 'border-gray-200 dark:border-slate-600 text-gray-600 dark:text-gray-400 hover:border-gray-300'"
            >
              🇨🇳 {{ tt('settings.langZh') }}
            </button>
            <button
              @click="switchLang('en')"
              class="flex-1 py-3 px-4 rounded-xl border-2 text-sm font-medium transition-all"
              :class="locale === 'en'
                ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                : 'border-gray-200 dark:border-slate-600 text-gray-600 dark:text-gray-400 hover:border-gray-300'"
            >
              🇺🇸 {{ tt('settings.langEn') }}
            </button>
          </div>
        </div>

        <!-- 外观（主题） -->
        <div class="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm">
          <h2 class="text-lg font-semibold text-gray-800 dark:text-white mb-4">{{ tt('settings.appearance') }}</h2>
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-700 dark:text-gray-300">{{ tt('settings.darkMode') }}</p>
              <p class="text-sm text-gray-500 dark:text-gray-400">{{ tt('settings.darkModeDesc') }}</p>
            </div>
            <div class="flex gap-1 bg-gray-100 dark:bg-stone-700 rounded-lg p-1">
              <button
                v-for="opt in themeOptions"
                :key="opt.value"
                class="px-3 py-1.5 rounded-md text-xs font-medium transition-all duration-200"
                :class="appStore.theme === opt.value
                  ? 'bg-white dark:bg-stone-600 text-amber-600 dark:text-amber-400 shadow-sm'
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'"
                @click="setTheme(opt.value)"
              >
                {{ opt.icon }} {{ opt.label }}
              </button>
            </div>
          </div>
        </div>

        <!-- 字体大小 -->
        <div class="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm">
          <h2 class="text-lg font-semibold text-gray-800 dark:text-white mb-4">{{ tt('settings.font') }} · {{ tt('settings.fontSize') }}</h2>
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">{{ tt('settings.fontSizeDesc') }}</p>
          <div class="flex gap-3">
            <button
              v-for="opt in fontSizeOptions"
              :key="opt.value"
              @click="setFontSize(opt.value)"
              class="flex-1 py-3 px-4 rounded-xl border-2 text-sm font-medium transition-all"
              :class="fontSize === opt.value
                ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                : 'border-gray-200 dark:border-slate-600 text-gray-600 dark:text-gray-400 hover:border-gray-300'"
            >
              {{ opt.label }}
            </button>
          </div>
          <!-- 预览 -->
          <div class="mt-4 p-4 bg-gray-50 dark:bg-slate-700/50 rounded-xl text-sm transition-all" :class="fontPreviewClass">
            <p class="font-semibold text-gray-700 dark:text-gray-300 mb-1">Aa</p>
            <p class="text-gray-500 dark:text-gray-400">预览字体大小 · The quick brown fox jumps over the lazy dog.</p>
          </div>
        </div>

        <!-- 代码字体 -->
        <div class="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm">
          <h2 class="text-lg font-semibold text-gray-800 dark:text-white mb-4">{{ tt('settings.codeFont') }}</h2>
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">{{ tt('settings.codeFontDesc') }}</p>
          <div class="flex gap-3">
            <button
              @click="setCodeFont('mono')"
              class="flex-1 py-3 px-4 rounded-xl border-2 text-sm font-medium transition-all"
              :class="codeFont === 'mono'
                ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                : 'border-gray-200 dark:border-slate-600 text-gray-600 dark:text-gray-400 hover:border-gray-300'"
            >
              <span class="font-mono">{{ tt('settings.codeFontMono') }}</span>
            </button>
            <button
              @click="setCodeFont('system')"
              class="flex-1 py-3 px-4 rounded-xl border-2 text-sm font-medium transition-all"
              :class="codeFont === 'system'
                ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                : 'border-gray-200 dark:border-slate-600 text-gray-600 dark:text-gray-400 hover:border-gray-300'"
            >
              {{ tt('settings.codeFontSystem') }}
            </button>
          </div>
          <div class="mt-4 p-4 bg-gray-50 dark:bg-slate-700/50 rounded-xl text-xs" :class="codeFont === 'system' ? '' : 'font-mono'">
            <code class="text-gray-600 dark:text-gray-400">const greeting = "Hello, World!";</code>
          </div>
        </div>

        <!-- 消息密度 -->
        <div class="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm">
          <h2 class="text-lg font-semibold text-gray-800 dark:text-white mb-4">{{ tt('settings.density') }}</h2>
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">{{ tt('settings.densityDesc') }}</p>
          <div class="flex gap-3">
            <button
              @click="setDensity('comfortable')"
              class="flex-1 py-3 px-4 rounded-xl border-2 text-sm font-medium transition-all"
              :class="density === 'comfortable'
                ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                : 'border-gray-200 dark:border-slate-600 text-gray-600 dark:text-gray-400 hover:border-gray-300'"
            >
              {{ tt('settings.densityComfortable') }}
            </button>
            <button
              @click="setDensity('compact')"
              class="flex-1 py-3 px-4 rounded-xl border-2 text-sm font-medium transition-all"
              :class="density === 'compact'
                ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                : 'border-gray-200 dark:border-slate-600 text-gray-600 dark:text-gray-400 hover:border-gray-300'"
            >
              {{ tt('settings.densityCompact') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAppStore } from '@/stores/app'
import type { ThemeMode } from '@/stores/app'
import { t } from '@/i18n'

const appStore = useAppStore()
const isDark = computed(() => appStore.isDark)
const locale = computed(() => appStore.locale)
const fontSize = computed(() => appStore.settings.fontSize)
const codeFont = computed(() => appStore.settings.codeFont)
const density = computed(() => appStore.settings.messageDensity)

const themeOptions = [
  { value: 'light' as ThemeMode, icon: '☀️', label: '浅色' },
  { value: 'dark' as ThemeMode, icon: '🌙', label: '深色' },
  { value: 'system' as ThemeMode, icon: '💻', label: '跟随系统' },
]

const fontSizeOptions = [
  { value: 'small', label: tt('settings.fontSmall') },
  { value: 'medium', label: tt('settings.fontMedium') },
  { value: 'large', label: tt('settings.fontLarge') },
] as const

const fontPreviewClass = computed(() => {
  const map = { small: 'text-xs', medium: 'text-sm', large: 'text-base' }
  return map[fontSize.value]
})

function tt(key: string) {
  return t(key, appStore.locale)
}

function switchLang(l: 'zh-CN' | 'en') {
  appStore.setLocale(l)
  window.location.reload()
}

function setTheme(t: ThemeMode) {
  appStore.theme = t
  appStore.settings.theme = t
  appStore.updateSettings()
}

function setFontSize(v: 'small' | 'medium' | 'large') {
  appStore.updateSettings({ fontSize: v })
}

function setCodeFont(v: 'mono' | 'system') {
  appStore.updateSettings({ codeFont: v })
}

function setDensity(v: 'comfortable' | 'compact') {
  appStore.updateSettings({ messageDensity: v })
}
</script>
