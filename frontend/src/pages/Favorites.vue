<template>
  <AppPage>
    <div class="p-6">
      <div class="flex items-center justify-between mb-6">
        <h1 class="text-2xl font-bold text-amber-900 dark:text-amber-100">⭐ 我的收藏</h1>
        <span class="text-sm text-amber-500 dark:text-amber-400">{{ favorites.length }} 张</span>
      </div>

      <AppEmpty v-if="favorites.length === 0 && !loading" emoji="⭐" title="还没有收藏的图片" description="在图片生成页点击 ⭐ 收藏" />

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="f in favorites" :key="f.id" class="group relative bg-white dark:bg-stone-800 rounded-2xl overflow-hidden shadow-sm hover:shadow-md transition-all border border-amber-200 dark:border-stone-700">
          <div class="aspect-square overflow-hidden cursor-pointer" @click="previewImage(f.imageUrl)">
            <img :src="f.imageUrl" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" alt="收藏的图片" />
          </div>
          <div class="p-3">
            <p class="text-sm text-amber-800 dark:text-amber-200 truncate">{{ f.prompt || '无提示词' }}</p>
            <div class="flex items-center gap-2 mt-1">
              <span v-if="f.style" class="text-xs px-2 py-0.5 rounded-full bg-amber-100 dark:bg-stone-700 text-amber-600 dark:text-amber-400">{{ f.style }}</span>
              <span v-if="f.ratio" class="text-xs px-2 py-0.5 rounded-full bg-amber-100 dark:bg-stone-700 text-amber-600 dark:text-amber-400">{{ f.ratio }}</span>
            </div>
          </div>
          <div class="absolute top-2 right-2 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <button @click.stop="removeFavorite(f.id)" class="w-8 h-8 rounded-full bg-white/90 dark:bg-stone-800/90 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 flex items-center justify-center shadow-sm transition-colors" title="取消收藏">
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
            </button>
          </div>
        </div>
      </div>

      <div v-if="loading" class="flex justify-center py-8">
        <AppSpinner size="md" />
      </div>
    </div>

    <AppLightbox v-model:visible="previewVisible" :src="previewUrl" downloadable />
  </AppPage>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { imageApi } from '@/services/api'
import AppPage from '@/components/AppPage.vue'
import AppEmpty from '@/components/AppEmpty.vue'
import AppSpinner from '@/components/AppSpinner.vue'
import AppLightbox from '@/components/AppLightbox.vue'

interface Favorite {
  id: number
  imageUrl: string
  prompt?: string
  style?: string
  ratio?: string
  created_at: string
}

const favorites = ref<Favorite[]>([])
const loading = ref(false)
const previewVisible = ref(false)
const previewUrl = ref('')

function previewImage(url: string) {
  previewUrl.value = url
  previewVisible.value = true
}

async function loadFavorites() {
  loading.value = true
  try {
    const res: any = await imageApi.getFavorites()
    const data = res.data?.data || res.data || []
    favorites.value = Array.isArray(data) ? data : []
  } catch {
    favorites.value = []
  } finally {
    loading.value = false
  }
}

async function removeFavorite(id: number) {
  try {
    await imageApi.removeFavorite(id)
    favorites.value = favorites.value.filter(f => f.id !== id)
  } catch (e) {
    console.error('取消收藏失败:', e)
  }
}

onMounted(() => {
  loadFavorites()
})
</script>