<template>
  <button :disabled="disabled || loading" :class="variantClass" class="rounded-xl font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed">
    <span v-if="loading" class="inline-flex items-center gap-2">
      <svg class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
      {{ loadingText || text }}
    </span>
    <span v-else>{{ text }}</span>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  text: string
  variant?: 'primary' | 'secondary' | 'danger'
  loading?: boolean
  disabled?: boolean
  loadingText?: string
  full?: boolean
}>(), { variant: 'primary', full: true })

const variantMap = {
  primary: 'bg-gradient-to-r from-amber-500 to-red-500 hover:from-amber-600 hover:to-red-600 text-white shadow-md hover:shadow-lg',
  secondary: 'bg-amber-100 dark:bg-stone-700 text-amber-800 dark:text-amber-200 hover:bg-amber-200 dark:hover:bg-stone-600',
  danger: 'bg-gradient-to-r from-red-500 to-rose-500 hover:from-red-600 hover:to-rose-600 text-white shadow-md',
}

const variantClass = computed(() => {
  const base = variantMap[props.variant]
  const width = props.full ? 'w-full py-2.5 px-4' : 'px-4 py-2'
  return `${base} ${width}`
})
</script>