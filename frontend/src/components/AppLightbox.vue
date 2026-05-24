<template>
  <Teleport to="body">
    <transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="visible" class="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center" style="z-index: 99999" @click="close">
        <img :src="src" class="max-w-[90vw] max-h-[90vh] object-contain rounded-lg shadow-2xl" @click.stop />
        <button @click="close" class="absolute top-4 right-4 w-10 h-10 rounded-full bg-white/10 hover:bg-white/20 text-white transition-colors flex items-center justify-center">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
        <button v-if="downloadable" @click.stop="doDownload" class="absolute bottom-6 right-6 w-10 h-10 rounded-full bg-white/10 hover:bg-white/20 text-white transition-colors flex items-center justify-center" title="下载">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
        </button>
      </div>
    </transition>
  </Teleport>
</template>

<script setup lang="ts">
import { downloadImage } from '@/composables/useImageDownload'

const props = defineProps<{
  visible: boolean
  src: string
  downloadable?: boolean
}>()

const emit = defineEmits<{ (e: 'update:visible', val: boolean): void }>()

function close() {
  emit('update:visible', false)
}

function doDownload() {
  downloadImage(props.src)
}
</script>