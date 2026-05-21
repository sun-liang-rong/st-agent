import axios from 'axios'
import type { TravelRequest, TravelResponse } from '@/types'

const api = axios.create({
  baseURL: '/api',
  timeout: 120000,
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export const apiService = {
  // ── 旅游攻略 ──
  generateTravel(request: TravelRequest): Promise<TravelResponse> {
    return api.post('/travel', request)
  },

  // ── AI 聊天 ──
  chat(message: string): Promise<{ reply: string }> {
    return api.post('/chat', { message })
  },

  // 聊天历史
  getChatHistory() {
    return api.get('/chat/history')
  },

  getChatHistoryDetail(id: string) {
    return api.get(`/chat/history/${id}`)
  },

  deleteChatHistory(id: string) {
    return api.delete(`/chat/history/${id}`)
  },

  // ── 用户 ──
  getSettings() {
    return api.get('/settings')
  },

  updateSettings(settings: any) {
    return api.put('/settings', settings)
  },

  // ── 历史记录 ──
  getHistory() {
    return api.get('/history')
  },

  deleteHistory(id: string) {
    return api.delete(`/history/${id}`)
  },
}

export default api
