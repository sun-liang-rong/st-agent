<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 via-white to-gray-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 px-4">
    <div class="text-center max-w-md animate-slide-in">
      <!-- 404 插图 -->
      <div class="mb-8 flex justify-center">
        <div class="relative">
          <svg class="w-40 h-40 text-gray-200 dark:text-slate-700" viewBox="0 0 200 200" fill="none">
            <circle cx="100" cy="100" r="90" stroke="currentColor" stroke-width="4" stroke-dasharray="8 8" opacity="0.4"/>
            <circle cx="100" cy="100" r="60" stroke="currentColor" stroke-width="3" stroke-dasharray="6 6" opacity="0.3"/>
            <text x="100" y="110" text-anchor="middle" fill="currentColor" font-size="56" font-weight="700" class="text-gray-300 dark:text-slate-600">404</text>
          </svg>
          <!-- 浮动装饰 -->
          <div class="absolute -top-2 -right-2 w-12 h-12 bg-primary-100 dark:bg-primary-900/30 rounded-full flex items-center justify-center animate-pulse">
            <svg class="w-6 h-6 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 1 1 7.072 0l-.548.547A3.374 3.374 0 0 0 14 18.469V19a2 2 0 1 1-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
            </svg>
          </div>
        </div>
      </div>

      <h1 class="text-2xl font-bold text-gray-800 dark:text-white mb-2">页面未找到</h1>
      <p class="text-gray-500 dark:text-gray-400 mb-8">你访问的页面不存在，可能已被移除或链接有误</p>

      <div class="flex gap-3 justify-center">
        <router-link
          to="/"
          class="inline-flex items-center gap-2 px-6 py-3 bg-primary-500 hover:bg-primary-600 text-white rounded-xl font-medium transition-all duration-200 hover:-translate-y-0.5 hover:shadow-lg shadow-primary-200 dark:shadow-primary-900/30"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
          </svg>
          返回首页
        </router-link>
        <button
          @click="router.back()"
          class="inline-flex items-center gap-2 px-6 py-3 bg-white dark:bg-slate-700 border border-gray-200 dark:border-slate-600 text-gray-700 dark:text-gray-300 rounded-xl font-medium hover:bg-gray-50 dark:hover:bg-slate-600 transition-all duration-200"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
          </svg>
          返回上页
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()
</script>
