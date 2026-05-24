<template>
  <AppPage>
    <div class="min-h-screen flex items-center justify-center p-4">
      <div class="w-full max-w-md">
        <div class="text-center mb-8">
          <div class="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-amber-500 to-red-500 flex items-center justify-center text-3xl shadow-lg mb-4">🤖</div>
          <h1 class="text-2xl font-bold text-amber-900 dark:text-amber-100">欢迎回来</h1>
          <p class="text-sm text-amber-500 dark:text-amber-400 mt-1">登录 ST-Agent</p>
        </div>

        <div class="bg-white dark:bg-stone-800 rounded-2xl shadow-lg border border-amber-200 dark:border-stone-700 p-6 space-y-4">
          <AppInput v-model="form.username" label="用户名" placeholder="请输入用户名" :required="true">
            <template #icon><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg></template>
          </AppInput>
          <AppInput v-model="form.password" label="密码" placeholder="请输入密码" type="password" :required="true">
            <template #icon><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg></template>
          </AppInput>

          <div v-if="error" class="text-sm text-red-500 bg-red-50 dark:bg-red-900/20 px-3 py-2 rounded-lg">{{ error }}</div>

          <AppBtn text="登录" :loading="loading" loading-text="登录中..." @click="handleLogin" />

          <div class="text-center">
            <router-link to="/register" class="text-sm text-amber-600 dark:text-amber-400 hover:text-amber-800 dark:hover:text-amber-200">还没有账号？注册</router-link>
          </div>
        </div>
      </div>
    </div>
  </AppPage>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AppPage from '@/components/AppPage.vue'
import AppInput from '@/components/AppInput.vue'
import AppBtn from '@/components/AppBtn.vue'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)
const error = ref('')

const form = reactive({ username: '', password: '' })

async function handleLogin() {
  if (!form.username || !form.password) { error.value = '请填写所有字段'; return }
  loading.value = true
  error.value = ''
  try {
    await authStore.login(form.username, form.password)
    router.push('/app')
  } catch (e: any) {
    error.value = e.response?.data?.detail || e.message || '登录失败'
  } finally { loading.value = false }
}
</script>