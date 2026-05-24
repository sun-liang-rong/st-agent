<template>
  <AppPage>
    <div class="max-w-2xl mx-auto p-6 space-y-6">
      <h1 class="text-2xl font-bold text-amber-900 dark:text-amber-100">⚙️ 个人中心</h1>

      <!-- Tabs -->
      <div class="grid grid-cols-2 gap-1 rounded-xl bg-amber-100/70 dark:bg-stone-800 p-1">
        <button v-for="tab in tabs" :key="tab.key" @click="activeTab = tab.key"
          class="rounded-lg px-4 py-2.5 text-sm font-medium transition-colors"
          :class="activeTab === tab.key ? 'bg-white text-amber-900 shadow-sm dark:bg-stone-700 dark:text-amber-100' : 'text-amber-600 hover:text-amber-900 dark:text-amber-400 dark:hover:text-amber-100'"
        >{{ tab.label }}</button>
      </div>

      <!-- Profile Tab -->
      <div v-if="activeTab === 'profile'" class="space-y-5">
        <div class="flex items-center gap-4">
          <div class="relative group">
            <div class="w-20 h-20 rounded-full bg-gradient-to-br from-amber-500 to-red-500 flex items-center justify-center text-3xl shadow-lg overflow-hidden">
              <img v-if="profile.avatarUrl" :src="profile.avatarUrl" class="w-full h-full object-cover" alt="avatar" />
              <span v-else>😊</span>
            </div>
            <label class="absolute inset-0 rounded-full bg-black/30 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center cursor-pointer">
              <span class="text-white text-xs">更换头像</span>
              <input type="file" accept="image/jpeg,image/png,image/webp" class="hidden" @change="onAvatarChange" />
            </label>
          </div>
          <div>
            <h2 class="text-lg font-bold text-amber-900 dark:text-amber-100">{{ profile.fullName || profile.username || '用户' }}</h2>
            <p class="text-sm text-amber-500 dark:text-amber-400">{{ profile.email }}</p>
          </div>
        </div>

        <div class="space-y-4">
          <AppInput v-model="profile.fullName" label="昵称" placeholder="请输入昵称" />
          <AppInput v-model="profile.email" label="邮箱" placeholder="请输入邮箱" type="email" />
          <AppBtn text="保存修改" :loading="saving" loading-text="保存中..." @click="saveProfile" />
        </div>

        <div class="border-t border-amber-200 dark:border-stone-700 pt-5">
          <h3 class="text-lg font-bold text-amber-900 dark:text-amber-100 mb-4">🔒 修改密码</h3>
          <div class="space-y-3">
            <AppInput v-model="passwords.old" label="旧密码" placeholder="旧密码" type="password" />
            <AppInput v-model="passwords.newPwd" label="新密码" placeholder="新密码（至少8位，包含字母和数字）" type="password" />
            <AppInput v-model="passwords.confirm" label="确认新密码" placeholder="确认新密码" type="password" />
            <AppBtn text="修改密码" variant="secondary" :loading="saving" loading-text="修改中..." @click="changePassword" />
          </div>
        </div>
      </div>

      <!-- Preferences Tab -->
      <div v-if="activeTab === 'preferences'" class="space-y-5">
        <div>
          <label class="block text-sm font-medium text-amber-800 dark:text-amber-200 mb-2">默认图片风格</label>
          <select v-model="preferences.defaultStyle" class="w-full rounded-xl border-2 border-amber-200 dark:border-stone-600 bg-white dark:bg-stone-800 px-4 py-2.5 text-sm text-amber-900 dark:text-amber-100 focus:outline-none focus:ring-2 focus:ring-amber-400">
            <option value="旅行海报">旅行海报</option>
            <option value="水墨画">水墨画</option>
            <option value="油画">油画</option>
            <option value="水彩画">水彩画</option>
            <option value="像素画">像素画</option>
            <option value="赛博朋克">赛博朋克</option>
            <option value="日系插画">日系插画</option>
            <option value="写实摄影">写实摄影</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-amber-800 dark:text-amber-200 mb-2">默认图片比例</label>
          <select v-model="preferences.defaultRatio" class="w-full rounded-xl border-2 border-amber-200 dark:border-stone-600 bg-white dark:bg-stone-800 px-4 py-2.5 text-sm text-amber-900 dark:text-amber-100 focus:outline-none focus:ring-2 focus:ring-amber-400">
            <option value="1:1">1:1</option>
            <option value="3:4">3:4</option>
            <option value="4:3">4:3</option>
            <option value="16:9">16:9</option>
            <option value="9:16">9:16</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-amber-800 dark:text-amber-200 mb-2">主题</label>
          <select v-model="preferences.theme" @change="applyTheme" class="w-full rounded-xl border-2 border-amber-200 dark:border-stone-600 bg-white dark:bg-stone-800 px-4 py-2.5 text-sm text-amber-900 dark:text-amber-100 focus:outline-none focus:ring-2 focus:ring-amber-400">
            <option value="light">浅色模式</option>
            <option value="dark">深色模式</option>
            <option value="system">跟随系统</option>
          </select>
        </div>
        <AppBtn text="保存偏好" @click="savePreferences" />
      </div>
    </div>
  </AppPage>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { authApi } from '@/services/auth'
import { useAppStore } from '@/stores/app'
import AppPage from '@/components/AppPage.vue'
import AppBtn from '@/components/AppBtn.vue'
import AppInput from '@/components/AppInput.vue'

const appStore = useAppStore()
const activeTab = ref<'profile' | 'preferences'>('profile')
const saving = ref(false)

const tabs = [
  { key: 'profile' as const, label: '👤 个人信息' },
  { key: 'preferences' as const, label: '🎨 偏好设置' },
]

const profile = reactive({ username: '', fullName: '', email: '', avatarUrl: '' })
const passwords = reactive({ old: '', newPwd: '', confirm: '' })
const preferences = reactive({ defaultStyle: '旅行海报', defaultRatio: '1:1', theme: 'light' })

async function loadProfile() {
  try {
    const data: any = await authApi.getCurrentUser()
    profile.username = data.username || ''
    profile.fullName = data.fullName || data.full_name || ''
    profile.email = data.email || ''
    profile.avatarUrl = data.avatarUrl || data.avatar_url || ''
  } catch (e) { console.error('加载个人信息失败:', e) }
}

async function saveProfile() {
  saving.value = true
  try {
    await authApi.updateProfile({ full_name: profile.fullName, email: profile.email })
    alert('保存成功')
  } catch (e: any) { alert('保存失败: ' + (e.response?.data?.detail || e.message)) }
  finally { saving.value = false }
}

async function onAvatarChange(e: Event) {
  const input = e.target as HTMLInputElement
  if (!input.files?.length) return
  const file = input.files[0]
  if (file.size > 2 * 1024 * 1024) { alert('文件大小不能超过2MB'); return }
  try {
    const res: any = await authApi.uploadAvatar(file)
    profile.avatarUrl = res.avatarUrl || res.avatar_url || profile.avatarUrl
  } catch (e: any) { alert('上传失败: ' + (e.response?.data?.detail || e.message)) }
}

async function changePassword() {
  if (passwords.newPwd !== passwords.confirm) { alert('两次输入的密码不一致'); return }
  if (passwords.newPwd.length < 8) { alert('新密码至少8位'); return }
  saving.value = true
  try {
    await authApi.changePassword({ old_password: passwords.old, new_password: passwords.newPwd })
    alert('密码修改成功')
    passwords.old = ''; passwords.newPwd = ''; passwords.confirm = ''
  } catch (e: any) { alert('修改失败: ' + (e.response?.data?.detail || e.message)) }
  finally { saving.value = false }
}

function applyTheme() { appStore.setTheme(preferences.theme as 'light' | 'dark' | 'system') }

function savePreferences() {
  localStorage.setItem('preferences', JSON.stringify(preferences))
  applyTheme()
  alert('偏好已保存')
}

onMounted(() => {
  loadProfile()
  const saved = localStorage.getItem('preferences')
  if (saved) {
    try {
      const p = JSON.parse(saved)
      preferences.defaultStyle = p.defaultStyle || '旅行海报'
      preferences.defaultRatio = p.defaultRatio || '1:1'
      preferences.theme = p.theme || 'light'
    } catch { /* ignore */ }
  }
})
</script>