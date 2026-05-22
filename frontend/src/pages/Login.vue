<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-amber-50 via-orange-50 to-yellow-50 dark:from-stone-900 dark:via-stone-800 dark:to-stone-900 py-12 px-4">
    <div class="w-full max-w-md">
      <!-- Logo & Title -->
      <div class="text-center mb-8">
        <div class="mx-auto w-16 h-16 bg-gradient-to-br from-amber-500 to-red-500 rounded-2xl shadow-lg flex items-center justify-center text-3xl hover:scale-105 transition-transform">
          🤖
        </div>
        <h2 class="mt-5 text-2xl font-bold text-amber-900 dark:text-amber-100">{{ tt('login.title') }}</h2>
        <p class="mt-1 text-sm text-amber-600 dark:text-amber-400">{{ tt('login.subtitle') }}</p>
      </div>

      <!-- Card -->
      <div class="bg-white dark:bg-stone-800 border-2 border-amber-200 dark:border-stone-700 rounded-2xl shadow-lg p-8">
        <form class="space-y-5" @submit.prevent="handleLogin">
          <!-- Username -->
          <div>
            <label class="block text-sm font-medium text-amber-800 dark:text-amber-200 mb-1.5">{{ tt('login.username') }}</label>
            <div class="relative">
              <span class="absolute inset-y-0 left-0 flex items-center pl-3.5 text-amber-400">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>
              </span>
              <input v-model="formData.username" type="text" required
                class="w-full pl-10 pr-4 py-2.5 bg-amber-50 dark:bg-stone-700 border-2 border-amber-200 dark:border-stone-600 text-amber-900 dark:text-amber-100 rounded-xl text-sm placeholder-amber-400 dark:placeholder-stone-500 focus:outline-none focus:ring-2 focus:ring-amber-400 focus:border-transparent transition-all"
                :placeholder="tt('login.username')" />
            </div>
          </div>

          <!-- Password -->
          <div>
            <label class="block text-sm font-medium text-amber-800 dark:text-amber-200 mb-1.5">{{ tt('login.password') }}</label>
            <div class="relative">
              <span class="absolute inset-y-0 left-0 flex items-center pl-3.5 text-amber-400">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>
              </span>
              <input v-model="formData.password" type="password" required
                class="w-full pl-10 pr-4 py-2.5 bg-amber-50 dark:bg-stone-700 border-2 border-amber-200 dark:border-stone-600 text-amber-900 dark:text-amber-100 rounded-xl text-sm placeholder-amber-400 dark:placeholder-stone-500 focus:outline-none focus:ring-2 focus:ring-amber-400 focus:border-transparent transition-all"
                :placeholder="tt('login.password')" />
            </div>
          </div>

          <!-- Remember -->
          <div class="flex items-center justify-between">
            <label class="flex items-center gap-2 cursor-pointer">
              <input v-model="formData.remember" type="checkbox"
                class="w-4 h-4 rounded border-amber-300 dark:border-stone-600 text-amber-600 focus:ring-amber-500 bg-amber-50 dark:bg-stone-700" />
              <span class="text-sm text-amber-700 dark:text-amber-300">{{ tt('login.remember') }}</span>
            </label>
          </div>

          <!-- Error -->
          <div v-if="errorMessage" class="flex items-start gap-2.5 p-3 bg-red-50 dark:bg-red-900/20 border-2 border-red-200 dark:border-red-800 rounded-xl">
            <svg class="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/></svg>
            <p class="text-sm text-red-700 dark:text-red-300">{{ errorMessage }}</p>
          </div>

          <!-- Submit -->
          <button type="submit" :disabled="loading"
            class="w-full py-2.5 px-4 bg-gradient-to-r from-amber-500 to-red-500 hover:from-amber-600 hover:to-red-600 text-white text-sm font-medium rounded-xl shadow-md hover:-translate-y-0.5 hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center gap-2">
            <svg v-if="loading" class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
            {{ loading ? tt('login.loading') : tt('login.submit') }}
          </button>
        </form>
      </div>

      <!-- Register Link -->
      <p class="text-center text-sm text-amber-600 dark:text-amber-400 mt-6">
        {{ tt('login.noAccount') }}
        <router-link to="/register" class="font-semibold text-amber-800 dark:text-amber-200 hover:text-red-500 dark:hover:text-red-400 transition-colors">{{ tt('login.register') }}</router-link>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAppStore } from '@/stores/app'
import { t } from '@/i18n'

const router = useRouter()
const authStore = useAuthStore()
const appStore = useAppStore()
const tt = (key: string) => t(key, appStore.locale)

const formData = ref({ username: '', password: '', remember: false })
const loading = ref(false)
const errorMessage = ref('')

async function handleLogin() {
  if (loading.value) return
  loading.value = true
  errorMessage.value = ''
  try {
    await authStore.login(formData.value.username, formData.value.password)
    router.push('/app')
  } catch (error: any) {
    errorMessage.value = error.response?.data?.detail || tt('login.error')
  } finally {
    loading.value = false
  }
}
</script>
