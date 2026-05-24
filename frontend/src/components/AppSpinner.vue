<template>
  <div :class="sizeClass" class="border-amber-200 border-t-amber-500 rounded-full animate-spin"></div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{ size?: 'sm' | 'md' | 'lg' }>(), { size: 'md' })

const sizeMap = { sm: 'w-6 h-6 border-2', md: 'w-10 h-10 border-2', lg: 'w-12 h-12 border-4' }
const sizeClass = computed(() => sizeMap[props.size])
</script>
