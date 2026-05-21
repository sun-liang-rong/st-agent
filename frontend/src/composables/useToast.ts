import { ref, type Ref } from 'vue'

export type ToastType = 'success' | 'error' | 'info' | 'warning'

export interface Toast {
  id: number
  type: ToastType
  message: string
  leaving: boolean
}

const toasts = ref<Toast[]>([]) as Ref<Toast[]>
let nextId = 1

const ICON_MAP: Record<ToastType, string> = {
  success: '✅',
  error: '❌',
  info: 'ℹ️',
  warning: '⚠️',
}

const BG_MAP: Record<ToastType, string> = {
  success: 'bg-green-50 dark:bg-green-900/30 border-green-200 dark:border-green-800 text-green-800 dark:text-green-200',
  error: 'bg-red-50 dark:bg-red-900/30 border-red-200 dark:border-red-800 text-red-800 dark:text-red-200',
  info: 'bg-blue-50 dark:bg-blue-900/30 border-blue-200 dark:border-blue-800 text-blue-800 dark:text-blue-200',
  warning: 'bg-amber-50 dark:bg-amber-900/30 border-amber-200 dark:border-amber-800 text-amber-800 dark:text-amber-200',
}

export function useToast() {
  function addToast(type: ToastType, message: string, duration = 3500) {
    const id = nextId++
    toasts.value.push({ id, type, message, leaving: false })

    setTimeout(() => {
      const toast = toasts.value.find(t => t.id === id)
      if (toast) toast.leaving = true
      setTimeout(() => {
        toasts.value = toasts.value.filter(t => t.id !== id)
      }, 300)
    }, duration)
  }

  function success(message: string) {
    addToast('success', message)
  }

  function error(message: string) {
    addToast('error', message, 5000)
  }

  function info(message: string) {
    addToast('info', message)
  }

  function warning(message: string) {
    addToast('warning', message)
  }

  function remove(id: number) {
    const toast = toasts.value.find(t => t.id === id)
    if (toast) toast.leaving = true
    setTimeout(() => {
      toasts.value = toasts.value.filter(t => t.id !== id)
    }, 300)
  }

  return { toasts, success, error, info, warning, remove, addToast, ICON_MAP, BG_MAP }
}
