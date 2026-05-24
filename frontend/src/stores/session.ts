import { defineStore } from 'pinia'
import { ref } from 'vue'
import { chatApi, type SessionInfo } from '@/services/api'

export const useSessionStore = defineStore('session', () => {
  const sessions = ref<SessionInfo[]>([])
  const loading = ref(false)
  const searchQuery = ref('')
  const searchResults = ref<SessionInfo[] | null>(null)
  const trashList = ref<SessionInfo[]>([])

  async function loadSessions() {
    loading.value = true
    try {
      const res: any = await chatApi.getSessions()
      sessions.value = Array.isArray(res) ? res : (res?.data ?? [])
    } catch {
      sessions.value = []
    } finally {
      loading.value = false
    }
  }

  function upsertSession(session: SessionInfo) {
    const idx = sessions.value.findIndex(s => s.contextId === session.contextId)
    if (idx >= 0) {
      sessions.value[idx] = session
    } else {
      sessions.value.unshift(session)
    }
  }

  async function searchSessions(q: string, limit = 20) {
    if (!q.trim()) {
      searchResults.value = null
      return
    }
    searchQuery.value = q
    try {
      const res: any = await chatApi.searchSessions(q, limit)
      searchResults.value = Array.isArray(res) ? res : (res?.data ?? [])
    } catch {
      searchResults.value = []
    }
  }

  function clearSearch() {
    searchQuery.value = ''
    searchResults.value = null
  }

  async function loadTrash() {
    try {
      const res: any = await chatApi.getTrash()
      trashList.value = Array.isArray(res) ? res : (res?.data ?? [])
    } catch {
      trashList.value = []
    }
  }

  async function restoreFromTrash(contextId: string) {
    await chatApi.restoreSession(contextId)
    trashList.value = trashList.value.filter(s => s.contextId !== contextId)
    await loadSessions()
  }

  async function permanentDelete(contextId: string) {
    await chatApi.permanentDelete(contextId)
    trashList.value = trashList.value.filter(s => s.contextId !== contextId)
  }

  async function clearAllTrash() {
    await chatApi.clearTrash()
    trashList.value = []
  }

  return {
    sessions,
    loading,
    searchQuery,
    searchResults,
    trashList,
    loadSessions,
    upsertSession,
    searchSessions,
    clearSearch,
    loadTrash,
    restoreFromTrash,
    permanentDelete,
    clearAllTrash,
  }
})