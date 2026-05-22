import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiService, type SessionItem } from '@/services/api'

export const useSessionStore = defineStore('session', () => {
  const sessions = ref<SessionItem[]>([])
  const loading = ref(false)

  async function loadSessions() {
    loading.value = true
    try {
      sessions.value = await apiService.getSessions()
    } catch {
      sessions.value = []
    } finally {
      loading.value = false
    }
  }

  function upsertSession(session: SessionItem) {
    const idx = sessions.value.findIndex(s => s.sessionId === session.sessionId)
    if (idx >= 0) {
      sessions.value[idx] = session
    } else {
      sessions.value.unshift(session)
    }
  }

  return {
    sessions,
    loading,
    loadSessions,
    upsertSession,
  }
})
