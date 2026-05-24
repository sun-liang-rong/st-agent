<template>
  <AppPage>
    <div class="max-w-3xl mx-auto p-6">
      <!-- Header -->
      <div class="text-center mb-8">
        <div class="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-amber-500 to-red-500 flex items-center justify-center text-3xl shadow-lg mb-4">🤖</div>
        <h1 class="text-2xl font-bold text-amber-900 dark:text-amber-100">ST-Agent 分享</h1>
      </div>

      <AppEmpty v-if="expired" emoji="⏰" title="该分享已过期" />
      <AppEmpty v-else-if="notFound" emoji="🔍" title="分享不存在" />

      <div v-else-if="shareData" class="bg-white dark:bg-stone-800 rounded-2xl shadow-lg border border-amber-200 dark:border-stone-700 overflow-hidden">
        <div v-if="shareData.imageUrl" class="w-full">
          <img :src="shareData.imageUrl" class="w-full object-cover max-h-[400px]" alt="分享图片" />
        </div>
        <div class="p-6">
          <h2 class="text-xl font-bold text-amber-900 dark:text-amber-100 mb-4">{{ shareData.title }}</h2>
          <div class="prose prose-amber dark:prose-invert max-w-none text-sm text-amber-800 dark:text-amber-200 whitespace-pre-wrap">{{ shareData.content }}</div>
        </div>
        <div class="px-6 py-4 border-t border-amber-200 dark:border-stone-700 flex items-center justify-between">
          <p class="text-xs text-amber-400 dark:text-stone-500">由 ST-Agent AI 智能生成</p>
          <span class="text-xs text-amber-400 dark:text-stone-500">{{ shareData.viewCount }} 次浏览</span>
        </div>
      </div>

      <div v-else class="flex justify-center py-16">
        <AppSpinner size="lg" />
      </div>
    </div>
  </AppPage>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { shareApi } from '@/services/api'
import AppPage from '@/components/AppPage.vue'
import AppEmpty from '@/components/AppEmpty.vue'
import AppSpinner from '@/components/AppSpinner.vue'

const route = useRoute()
const shareData = ref<any>(null)
const expired = ref(false)
const notFound = ref(false)

onMounted(async () => {
  const token = route.params.token as string
  if (!token) {
    notFound.value = true
    return
  }
  try {
    const res: any = await shareApi.getContent(token)
    shareData.value = res.data || res
  } catch (e: any) {
    if (e.response?.status === 410) {
      expired.value = true
    } else {
      notFound.value = true
    }
  }
})
</script>