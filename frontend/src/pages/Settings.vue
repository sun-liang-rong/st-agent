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

        <!-- 主题 -->
        <div class="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm">
          <h2 class="text-lg font-semibold text-gray-800 dark:text-white mb-4">{{ tt('settings.appearance') }}</h2>
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-700 dark:text-gray-300">{{ tt('settings.darkMode') }}</p>
              <p class="text-sm text-gray-500 dark:text-gray-400">{{ tt('settings.darkModeDesc') }}</p>
            </div>
            <button
              @click="toggleTheme"
              class="w-14 h-7 rounded-full transition-colors"
              :class="isDark ? 'bg-primary-500' : 'bg-gray-300'"
            >
              <div
                class="w-5 h-5 bg-white rounded-full shadow transform transition-transform"
                :class="isDark ? 'translate-x-8' : 'translate-x-1'"
              />
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
import { t } from '@/i18n'

const appStore = useAppStore()
const isDark = computed(() => appStore.isDark)
const locale = computed(() => appStore.locale)

function tt(key: string) {
  return t(key, appStore.locale)
}

function switchLang(l: 'zh-CN' | 'en') {
  appStore.setLocale(l)
  // 刷新页面使所有组件的翻译生效
  window.location.reload()
}

function toggleTheme() {
  appStore.toggleTheme()
}
</script>
