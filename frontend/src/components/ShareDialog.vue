<template>
  <Teleport to="body">
    <transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="visible" class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center" style="z-index: 99998" @click="close">
        <div class="bg-white dark:bg-stone-800 rounded-2xl shadow-xl border border-amber-200 dark:border-stone-700 w-[90vw] max-w-md p-6" @click.stop>
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-bold text-amber-900 dark:text-amber-100">🔗 分享</h3>
            <button @click="close" class="w-8 h-8 rounded-full hover:bg-amber-100 dark:hover:bg-stone-700 flex items-center justify-center text-amber-500 transition-colors">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </button>
          </div>

          <!-- Share type selector -->
          <div v-if="!shareLink" class="space-y-3">
            <div class="flex items-center gap-2 text-sm text-amber-700 dark:text-amber-300 mb-2">有效期</div>
            <div class="grid grid-cols-3 gap-2 mb-4">
              <button v-for="opt in expireOptions" :key="opt.value" @click="expiresInHours = opt.value"
                class="px-3 py-2 rounded-xl text-sm font-medium transition-colors"
                :class="expiresInHours === opt.value ? 'bg-amber-500 text-white shadow-md' : 'bg-amber-50 dark:bg-stone-700 text-amber-800 dark:text-amber-200 hover:bg-amber-100 dark:hover:bg-stone-600'"
              >{{ opt.label }}</button>
            </div>
            <button @click="createShare" :disabled="creating" class="w-full py-2.5 rounded-xl bg-gradient-to-r from-amber-500 to-red-500 text-white font-medium shadow-md hover:shadow-lg transition-all disabled:opacity-50">
              {{ creating ? '创建中...' : '创建分享链接' }}
            </button>
          </div>

          <!-- Share result -->
          <div v-else class="space-y-4">
            <div class="flex items-center gap-2 bg-amber-50 dark:bg-stone-700 rounded-xl px-4 py-3">
              <input :value="shareLink" readonly class="flex-1 bg-transparent text-sm text-amber-900 dark:text-amber-100 focus:outline-none truncate" />
              <button @click="copyLink" class="text-xs px-3 py-1.5 rounded-lg bg-amber-500 text-white hover:bg-amber-600 transition-colors flex-shrink-0">
                {{ copied ? '✓ 已复制' : '复制' }}
              </button>
            </div>
            <div class="flex gap-2">
              <button @click="shareLink = ''; copied = false" class="flex-1 py-2 rounded-xl bg-amber-50 dark:bg-stone-700 text-amber-800 dark:text-amber-200 text-sm font-medium hover:bg-amber-100 dark:hover:bg-stone-600 transition-colors">
                重新创建
              </button>
              <button @click="close" class="flex-1 py-2 rounded-xl bg-gradient-to-r from-amber-500 to-red-500 text-white text-sm font-medium shadow-md hover:shadow-lg transition-all">
                完成
              </button>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { shareApi } from '@/services/api'

const props = defineProps<{
  visible: boolean
  type: 'travel' | 'image'
  contentId: string
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const expiresInHours = ref(24)
const creating = ref(false)
const shareLink = ref('')
const copied = ref(false)

const expireOptions = [
  { value: 1, label: '1小时' },
  { value: 24, label: '1天' },
  { value: 168, label: '7天' },
]

function close() {
  shareLink.value = ''
  copied.value = false
  emit('close')
}

async function createShare() {
  creating.value = true
  try {
    const res: any = await shareApi.create({
      type: props.type,
      contentId: props.contentId,
      expiresInHours: expiresInHours.value,
    })
    const token = res.shareToken || res.share_token || res.token
    shareLink.value = `${window.location.origin}/share/${token}`
  } catch (e: any) {
    alert('创建分享失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    creating.value = false
  }
}

function copyLink() {
  navigator.clipboard.writeText(shareLink.value)
  copied.value = true
  setTimeout(() => { copied.value = false }, 2000)
}
</script>