<template>
  <div class="bg-white dark:bg-slate-800 rounded-xl border border-gray-100 dark:border-slate-700/50 shadow-sm overflow-hidden transition-all hover:shadow-md"
       :class="sizeClass">
    <div class="px-4 pt-4 pb-2">
      <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-200">{{ title }}</h3>
    </div>
    <div class="px-2 pb-2">
      <div v-if="error" class="flex flex-col items-center justify-center h-48 text-center px-4">
        <svg class="w-8 h-8 text-red-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"/>
        </svg>
        <p class="text-xs text-red-500 dark:text-red-400">{{ error }}</p>
      </div>
      <v-chart v-else ref="chartRef" :option="option" :autoresize="true" style="height: 280px; width: 100%;" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, LineChart, PieChart, ScatterChart, RadarChart, FunnelChart, HeatmapChart, TreemapChart } from 'echarts/charts'
import {
  TitleComponent, TooltipComponent, LegendComponent, GridComponent,
  DatasetComponent, TransformComponent, ToolboxComponent, DataZoomComponent,
  VisualMapComponent,
} from 'echarts/components'

use([
  CanvasRenderer,
  BarChart, LineChart, PieChart, ScatterChart, RadarChart, FunnelChart, HeatmapChart, TreemapChart,
  TitleComponent, TooltipComponent, LegendComponent, GridComponent,
  DatasetComponent, TransformComponent, ToolboxComponent, DataZoomComponent,
  VisualMapComponent,
])

const props = defineProps<{
  title: string
  option: Record<string, any>
  size?: 'full' | 'half' | 'third'
}>()

const chartRef = ref<InstanceType<typeof VChart> | null>(null)
const error = ref<string>('')

const sizeClass = computed(() => {
  switch (props.size) {
    case 'full': return 'col-span-1 md:col-span-2'
    case 'third': return 'col-span-1'
    case 'half':
    default: return 'col-span-1'
  }
})

function validateOption(opt: Record<string, any>): string {
  if (!opt || typeof opt !== 'object') return '图表配置不是对象'
  if (!opt.series) return '缺少 series 字段'
  return ''
}

onMounted(() => {
  error.value = validateOption(props.option)
})

watch(() => props.option, (newOpt) => {
  error.value = validateOption(newOpt)
}, { deep: true })
</script>
