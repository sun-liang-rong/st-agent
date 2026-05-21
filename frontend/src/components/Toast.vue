<template>
  <Teleport to="body">
    <div class="toast-container">
      <TransitionGroup name="toast">
        <div
          v-for="toast in toasts"
          :key="toast.id"
          :class="[
            'toast-item',
            toast.leaving ? 'animate-toast-out' : 'animate-toast-in',
            BG_MAP[toast.type]
          ]"
          @click="remove(toast.id)"
        >
          <span class="text-base leading-none flex-shrink-0">{{ ICON_MAP[toast.type] }}</span>
          <span class="text-sm leading-tight flex-1 min-w-0">{{ toast.message }}</span>
          <button
            @click.stop="remove(toast.id)"
            class="flex-shrink-0 p-0.5 rounded hover:opacity-70 transition-opacity"
          >
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { useToast } from '@/composables/useToast'

const { toasts, remove, ICON_MAP, BG_MAP } = useToast()
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 1rem;
  right: 1rem;
  z-index: 99999;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-width: 400px;
  pointer-events: none;
}

.toast-item {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.75rem 1rem;
  border-radius: 12px;
  border-width: 1px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1), 0 1px 3px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  pointer-events: auto;
  backdrop-filter: blur(8px);
}

.animate-toast-in {
  animation: toastSlideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.animate-toast-out {
  animation: toastSlideOut 0.25s ease-in forwards;
}

.toast-enter-active {
  animation: toastSlideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.toast-leave-active {
  animation: toastSlideOut 0.25s ease-in;
}

@keyframes toastSlideIn {
  from {
    opacity: 0;
    transform: translateX(100%) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateX(0) scale(1);
  }
}

@keyframes toastSlideOut {
  from {
    opacity: 1;
    transform: translateX(0) scale(1);
  }
  to {
    opacity: 0;
    transform: translateX(100%) scale(0.95);
  }
}
</style>
