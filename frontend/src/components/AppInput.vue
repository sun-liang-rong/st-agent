<template>
  <div>
    <label v-if="label" class="block text-sm font-medium text-amber-800 dark:text-amber-200 mb-1">{{ label }}</label>
    <div class="relative">
      <span v-if="$slots.icon" class="absolute inset-y-0 left-0 flex items-center pl-3.5 text-amber-400">
        <slot name="icon" />
      </span>
      <input
        v-model="modelValue"
        :type="type"
        :placeholder="placeholder"
        :required="required"
        :class="inputClass"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  label?: string
  type?: string
  placeholder?: string
  required?: boolean
}>(), { type: 'text', required: false })

const modelValue = defineModel<string>()

const inputClass = computed(() => {
  const base = 'w-full rounded-xl border-2 border-amber-200 dark:border-stone-600 bg-white dark:bg-stone-800 px-4 py-2.5 text-sm text-amber-900 dark:text-amber-100 focus:outline-none focus:ring-2 focus:ring-amber-400 placeholder-amber-400 dark:placeholder-stone-500'
  return base
})
</script>