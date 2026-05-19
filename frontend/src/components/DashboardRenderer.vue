<template>
  <div class="space-y-4">
    <div v-if="spec.title" class="mb-2">
      <h2 class="text-lg font-bold text-gray-800 dark:text-white">{{ spec.title }}</h2>
      <p v-if="spec.description" class="text-sm text-gray-500 dark:text-gray-400 mt-1">{{ spec.description }}</p>
    </div>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <ChartCard
        v-for="chart in spec.charts"
        :key="chart.id"
        :title="chart.title"
        :option="chart.option"
        :size="chart.size"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { DashboardSpec } from '@/types'
import ChartCard from './ChartCard.vue'

defineProps<{
  spec: DashboardSpec
}>()
</script>
