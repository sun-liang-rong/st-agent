<template>
  <div class="flex flex-col items-center py-16 text-center">
    <div class="text-5xl mb-4 opacity-40">{{ emoji }}</div>
    <p class="text-amber-500 dark:text-amber-400">{{ title }}</p>
    <p v-if="description" class="text-sm text-amber-400 dark:text-stone-500 mt-1">{{ description }}</p>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  emoji: string
  title: string
  description?: string
}>()
</script>
