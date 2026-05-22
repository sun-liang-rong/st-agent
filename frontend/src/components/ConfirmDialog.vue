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
      <div v-if="visible" class="fixed inset-0 bg-black/30 backdrop-blur-sm flex items-center justify-center" style="z-index: 99999" @click="handleCancel">
        <transition
          enter-active-class="transition duration-200 ease-out"
          enter-from-class="opacity-0 scale-95"
          enter-to-class="opacity-100 scale-100"
          leave-active-class="transition duration-150 ease-in"
          leave-from-class="opacity-100 scale-100"
          leave-to-class="opacity-0 scale-95"
        >
          <div v-if="visible" class="bg-white dark:bg-stone-800 border-2 border-amber-200 dark:border-stone-600 rounded-2xl shadow-2xl p-6 w-[340px] max-w-[90vw]" @click.stop>
            <!-- Icon -->
            <div class="flex justify-center mb-4">
              <div class="w-14 h-14 rounded-full flex items-center justify-center" :class="currentIconBg">
                <span class="text-2xl">{{ currentIcon }}</span>
              </div>
            </div>
            <!-- Title -->
            <h3 class="text-base font-semibold text-center text-amber-900 dark:text-amber-100 mb-2">{{ title }}</h3>
            <!-- Message -->
            <p v-if="message" class="text-sm text-center text-amber-600 dark:text-amber-400 mb-6">{{ message }}</p>
            <div v-else class="mb-6"></div>
            <!-- Actions -->
            <div class="flex gap-3">
              <button
                @click="handleCancel"
                class="flex-1 px-4 py-2.5 rounded-xl text-sm font-medium border-2 border-amber-200 dark:border-stone-600 text-amber-700 dark:text-amber-300 hover:bg-amber-50 dark:hover:bg-stone-700 transition-colors"
              >
                取消
              </button>
              <button
                @click="handleConfirm"
                class="flex-1 px-4 py-2.5 rounded-xl text-sm font-medium text-white transition-colors shadow-md"
                :class="currentBtnClass"
              >
                {{ confirmText }}
              </button>
            </div>
          </div>
        </transition>
      </div>
    </transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

interface ConfirmOptions {
  title?: string
  message?: string
  icon?: string
  confirmText?: string
  type?: 'danger' | 'warning' | 'info'
}

const visible = ref(false)
const title = ref('确认操作')
const message = ref('')
const confirmText = ref('确认')
const currentType = ref<'danger' | 'warning' | 'info'>('danger')

let resolveFn: ((value: boolean) => void) | null = null

const typeConfig = {
  danger: {
    icon: '🗑️',
    iconBg: 'bg-red-100 dark:bg-red-900/30',
    btnClass: 'bg-gradient-to-r from-red-500 to-rose-500 hover:from-red-600 hover:to-rose-600',
  },
  warning: {
    icon: '⚠️',
    iconBg: 'bg-amber-100 dark:bg-amber-900/30',
    btnClass: 'bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600',
  },
  info: {
    icon: 'ℹ️',
    iconBg: 'bg-amber-100 dark:bg-amber-900/30',
    btnClass: 'bg-gradient-to-r from-amber-500 to-red-500 hover:from-amber-600 hover:to-red-600',
  },
}

const currentIcon = computed(() => typeConfig[currentType.value].icon)
const currentIconBg = computed(() => typeConfig[currentType.value].iconBg)
const currentBtnClass = computed(() => typeConfig[currentType.value].btnClass)

function confirm(options: ConfirmOptions = {}): Promise<boolean> {
  currentType.value = options.type || 'danger'
  title.value = options.title || '确认删除'
  message.value = options.message || ''
  confirmText.value = options.confirmText || '删除'
  visible.value = true

  return new Promise((resolve) => {
    resolveFn = resolve
  })
}

function handleConfirm() {
  visible.value = false
  resolveFn?.(true)
  resolveFn = null
}

function handleCancel() {
  visible.value = false
  resolveFn?.(false)
  resolveFn = null
}

defineExpose({ confirm })
</script>
