<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-amber-50 via-orange-50 to-yellow-50 dark:from-stone-900 dark:via-stone-800 dark:to-stone-900 py-12 px-4">
    <div class="w-full max-w-md">
      <!-- Logo & Title -->
      <div class="text-center mb-8">
        <div class="mx-auto w-16 h-16 bg-gradient-to-br from-amber-500 to-red-500 rounded-2xl shadow-lg flex items-center justify-center text-3xl hover:scale-105 transition-transform">
          🤖
        </div>
        <h2 class="mt-5 text-2xl font-bold text-amber-900 dark:text-amber-100">{{ tt('register.title') }}</h2>
        <p class="mt-1 text-sm text-amber-600 dark:text-amber-400">{{ tt('register.subtitle') }}</p>
      </div>

      <!-- Card -->
      <div class="bg-white dark:bg-stone-800 border-2 border-amber-200 dark:border-stone-700 rounded-2xl shadow-lg p-8">
        <form class="space-y-5" @submit.prevent="handleRegister">
          <!-- Username -->
          <div>
            <label class="block text-sm font-medium text-amber-800 dark:text-amber-200 mb-1.5">{{ tt('register.username') }}</label>
            <div class="relative">
              <span class="absolute inset-y-0 left-0 flex items-center pl-3.5 text-amber-400">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>
              </span>
              <input v-model="formData.username" type="text" required
                class="w-full pl-10 pr-4 py-2.5 bg-amber-50 dark:bg-stone-700 border-2 border-amber-200 dark:border-stone-600 text-amber-900 dark:text-amber-100 rounded-xl text-sm placeholder-amber-400 dark:placeholder-stone-500 focus:outline-none focus:ring-2 focus:ring-amber-400 focus:border-transparent transition-all"
                :placeholder="tt('register.username')" />
            </div>
          </div>

          <!-- Email -->
          <div>
            <label class="block text-sm font-medium text-amber-800 dark:text-amber-200 mb-1.5">{{ tt('register.email') }}</label>
            <div class="relative">
              <span class="absolute inset-y-0 left-0 flex items-center pl-3.5 text-amber-400">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>
              </span>
              <input v-model="formData.email" type="email" required
                class="w-full pl-10 pr-4 py-2.5 bg-amber-50 dark:bg-stone-700 border-2 border-amber-200 dark:border-stone-600 text-amber-900 dark:text-amber-100 rounded-xl text-sm placeholder-amber-400 dark:placeholder-stone-500 focus:outline-none focus:ring-2 focus:ring-amber-400 focus:border-transparent transition-all"
                :placeholder="tt('register.email')" />
            </div>
          </div>

          <!-- Password -->
          <div>
            <label class="block text-sm font-medium text-amber-800 dark:text-amber-200 mb-1.5">{{ tt('register.password') }}</label>
            <div class="relative">
              <span class="absolute inset-y-0 left-0 flex items-center pl-3.5 text-amber-400">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>
              </span>
              <input v-model="formData.password" type="password" required
                class="w-full pl-10 pr-4 py-2.5 bg-amber-50 dark:bg-stone-700 border-2 border-amber-200 dark:border-stone-600 text-amber-900 dark:text-amber-100 rounded-xl text-sm placeholder-amber-400 dark:placeholder-stone-500 focus:outline-none focus:ring-2 focus:ring-amber-400 focus:border-transparent transition-all"
                :placeholder="tt('register.password')" />
            </div>
          </div>

          <!-- Confirm Password -->
          <div>
            <label class="block text-sm font-medium text-amber-800 dark:text-amber-200 mb-1.5">{{ tt('register.confirmPassword') }}</label>
            <div class="relative">
              <span class="absolute inset-y-0 left-0 flex items-center pl-3.5 text-amber-400">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>
              </span>
              <input v-model="formData.confirmPassword" type="password" required
                class="w-full pl-10 pr-4 py-2.5 bg-amber-50 dark:bg-stone-700 border-2 border-amber-200 dark:border-stone-600 text-amber-900 dark:text-amber-100 rounded-xl text-sm placeholder-amber-400 dark:placeholder-stone-500 focus:outline-none focus:ring-2 focus:ring-amber-400 focus:border-transparent transition-all"
                :placeholder="tt('register.confirmPassword')" />
            </div>
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
            {{ loading ? tt('register.loading') : tt('register.submit') }}
          </button>
        </form>
      </div>

      <!-- Login Link -->
      <p class="text-center text-sm text-amber-600 dark:text-amber-400 mt-6">
        {{ tt('register.hasAccount') }}
        <router-link to="/login" class="font-semibold text-amber-800 dark:text-amber-200 hover:text-red-500 dark:hover:text-red-400 transition-colors">{{ tt('register.login') }}</router-link>
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

const formData = ref({ username: '', email: '', password: '', confirmPassword: '' })
const loading = ref(false)
const errorMessage = ref('')

async function handleRegister() {
  if (loading.value) return
  if (formData.value.password !== formData.value.confirmPassword) {
    errorMessage.value = tt('register.passwordMismatch')
    return
  }
  loading.value = true
  errorMessage.value = ''
  try {
    await authStore.register(formData.value.username, formData.value.email, formData.value.password)
    router.push('/login')
  } catch (error: any) {
    errorMessage.value = error.response?.data?.detail || tt('register.error')
  } finally {
    loading.value = false
  }
}
</script>
