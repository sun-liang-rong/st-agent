<template>
  <div class="flex flex-col h-full bg-gradient-to-br from-amber-50 via-orange-50 to-yellow-50 dark:from-stone-900 dark:via-stone-800 dark:to-stone-900">
    <!-- Header -->
    <div class="px-6 py-4 border-b border-amber-200 dark:border-stone-700">
      <h1 class="text-xl font-bold text-amber-800 dark:text-amber-200">🎨 AI 图片生成</h1>
      <p class="text-sm text-amber-600 dark:text-amber-400 mt-1">输入提示词，让 AI 为你创作</p>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto p-6">
      <!-- Empty State -->
      <div v-if="items.length === 0 && !loading" class="flex flex-col items-center justify-center py-16 text-center">
        <div class="text-5xl mb-4">🎨</div>
        <div class="text-lg font-semibold text-amber-800 dark:text-amber-200 mb-2">输入提示词，生成图片</div>
        <div class="text-sm text-amber-600 dark:text-amber-400">试试描述一个场景，我来帮你画出来</div>
      </div>

      <!-- Image Gallery Grid -->
      <div v-else class="grid grid-cols-2 md:grid-cols-3 gap-4">
        <!-- Skeleton Card -->
        <div v-if="loading" class="bg-white dark:bg-stone-800 border-2 border-dashed border-amber-300 dark:border-stone-600 rounded-2xl overflow-hidden">
          <div class="w-full aspect-square bg-gradient-to-br from-amber-100 to-orange-100 dark:from-stone-700 dark:to-stone-600 flex items-center justify-center animate-pulse">
            <span class="text-2xl">✨</span>
          </div>
          <div class="p-3">
            <div class="h-4 bg-amber-100 dark:bg-stone-700 rounded w-3/4"></div>
          </div>
        </div>

        <!-- Image Cards -->
        <div v-for="it in items" :key="it.id" class="bg-white dark:bg-stone-800 border-2 border-amber-300 dark:border-stone-600 rounded-2xl overflow-hidden shadow-sm hover:shadow-md hover:scale-[1.02] transition-all duration-200 group">
          <div class="relative">
            <img v-if="it.imageUrl" :src="it.imageUrl" class="w-full aspect-square object-cover" alt="generated" />
            <div v-else class="w-full aspect-square bg-gradient-to-br from-amber-100 to-orange-100 dark:from-stone-700 dark:to-stone-600 flex items-center justify-center text-4xl">🎨</div>
            <!-- Hover Actions -->
            <div v-if="it.imageUrl" class="absolute bottom-3 right-3 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
              <button @click="downloadImage(it.imageUrl)" class="w-8 h-8 rounded-full bg-white/90 dark:bg-stone-700/90 shadow flex items-center justify-center text-sm hover:bg-white" title="下载">⬇️</button>
              <button @click="regenerate(it.prompt)" class="w-8 h-8 rounded-full bg-white/90 dark:bg-stone-700/90 shadow flex items-center justify-center text-sm hover:bg-white" title="重新生成">🔄</button>
            </div>
          </div>
          <div class="p-3">
            <p class="text-sm text-amber-800 dark:text-amber-200 truncate">{{ it.prompt }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Input Area -->
    <div class="p-4 border-t border-amber-200 dark:border-stone-700">
      <!-- Prompt Inspiration -->
      <div v-if="items.length === 0 && !loading" class="flex gap-2 flex-wrap mb-3 max-w-3xl mx-auto">
        <span class="text-xs text-amber-600 dark:text-amber-400 self-center">💡 试试：</span>
        <button @click="fillPrompt('日落下的古镇，水墨画风格')" class="bg-white dark:bg-stone-800 border-2 border-amber-300 dark:border-stone-600 rounded-full px-3 py-1.5 text-xs text-amber-800 dark:text-amber-200 hover:-translate-y-0.5 hover:shadow-md transition-all">🌅 日落古镇</button>
        <button @click="fillPrompt('雪山湖泊倒影，写实摄影')" class="bg-white dark:bg-stone-800 border-2 border-amber-300 dark:border-stone-600 rounded-full px-3 py-1.5 text-xs text-amber-800 dark:text-amber-200 hover:-translate-y-0.5 hover:shadow-md transition-all">🏔️ 雪山湖泊</button>
        <button @click="fillPrompt('樱花小径，日系插画')" class="bg-white dark:bg-stone-800 border-2 border-amber-300 dark:border-stone-600 rounded-full px-3 py-1.5 text-xs text-amber-800 dark:text-amber-200 hover:-translate-y-0.5 hover:shadow-md transition-all">🌸 樱花小径</button>
      </div>
      <div class="flex gap-3 items-end max-w-3xl mx-auto">
        <textarea
          v-model="input"
          @keydown.enter.ctrl="generate"
          :disabled="loading"
          placeholder="描述你想要的图片..."
          rows="2"
          class="flex-1 border-2 border-amber-300 dark:border-stone-600 bg-white dark:bg-stone-800 rounded-2xl px-4 py-3 text-sm text-amber-900 dark:text-amber-100 placeholder-amber-400 dark:placeholder-stone-500 focus:outline-none focus:ring-2 focus:ring-amber-400 focus:border-transparent resize-none disabled:opacity-50"
        ></textarea>
        <button
          @click="generate"
          :disabled="loading || !input.trim()"
          class="px-5 py-3 rounded-xl bg-gradient-to-r from-amber-500 to-red-500 hover:from-amber-600 hover:to-red-600 text-white font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md hover:shadow-lg"
        >
          {{ loading ? '生成中...' : '生成' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { apiService } from '../services/api'

const input = ref('')
const loading = ref(false)
const items = ref<any[]>([])

async function generate() {
  const prompt = input.value.trim()
  if (!prompt || loading.value) return

  loading.value = true
  try {
    const res = await apiService.generateImage(prompt)
    items.value.unshift({
      id: Date.now(),
      prompt,
      imageUrl: res.image_url || res.url,
    })
    input.value = ''
  } catch (e) {
    console.error('Image generation failed:', e)
  } finally {
    loading.value = false
  }
}

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

function fillPrompt(text: string) {
  input.value = text
}
</script>
