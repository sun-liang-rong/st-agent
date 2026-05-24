import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || '/api'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

// 请求拦截：附加 token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// 响应拦截：401 跳转登录
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  },
)

// ─── 认证 ────────────────────────────────────────────────────

export const authApi = {
  register: (data: { username: string; password: string }) =>
    api.post('/auth/register', data),
  login: (data: { username: string; password: string }) =>
    api.post('/auth/login', data),
  getMe: () => api.get('/auth/me'),
  updateProfile: (data: { full_name?: string; email?: string }) =>
    api.put('/auth/profile', data),
  changePassword: (data: { old_password: string; new_password: string }) =>
    api.put('/auth/password', data),
  uploadAvatar: (file: File) => {
    const fd = new FormData()
    fd.append('file', file)
    return api.post('/auth/avatar', fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}

// ─── 聊天 ────────────────────────────────────────────────────

export interface ChatMessage {
  id: number
  contextId: string
  title?: string
  userMessage: string
  aiReply: string
  sessionType: string
  imageUrl?: string
  imageRatio?: string
  createdAt: string
}

export interface SessionInfo {
  contextId: string
  title: string
  summary?: string
  sessionType: string
  updatedAt: string
}

export const chatApi = {
  /** 获取会话列表 */
  getSessions: () => api.get<SessionInfo[]>('/chat/sessions'),

  /** 搜索会话 */
  searchSessions: (q: string, limit = 20) =>
    api.get('/chat/sessions/search', { params: { q, limit } }),

  /** 获取会话详情 */
  getSessionDetail: (contextId: string) =>
    api.get<ChatMessage[]>(`/chat/session/${contextId}`),

  /** 删除会话（软删除） */
  deleteSession: (contextId: string) =>
    api.delete(`/chat/session/${contextId}`),

  /** 重命名会话 */
  renameSession: (contextId: string, title: string) =>
    api.patch(`/chat/session/${contextId}`, { title }),

  /** 流式聊天（SSE） */
  streamChat: (
    message: string,
    contextId?: string,
    options?: { generateImage?: boolean; imageStyle?: string; imageRatio?: string },
  ) => {
    const token = localStorage.getItem('token')
    const body: Record<string, unknown> = { message, contextId }
    if (options?.generateImage) body.generateImage = true
    if (options?.imageStyle) body.imageStyle = options.imageStyle
    if (options?.imageRatio) body.imageRatio = options.imageRatio
    return fetch(`${API_BASE}/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify(body),
    })
  },

  /** 流式重新生成（SSE） */
  streamRegenerate: (messageId: number) => {
    const token = localStorage.getItem('token')
    return fetch(`${API_BASE}/chat/regenerate/${messageId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
    })
  },

  // ─── 回收站 ─────────────────────────────────────────────────

  getTrash: () => api.get('/chat/trash'),

  restoreSession: (contextId: string) =>
    api.post(`/chat/trash/${contextId}/restore`),

  permanentDelete: (contextId: string) =>
    api.delete(`/chat/trash/${contextId}`),

  clearTrash: () => api.delete('/chat/trash'),
}

// ─── 图片生成 ────────────────────────────────────────────────

export const imageApi = {
  /** SSE 流式图片生成 */
  streamGenerate: (prompt: string, style: string, ratio: string, contextId?: string) => {
    const token = localStorage.getItem('token')
    return fetch(`${API_BASE}/image/generate/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({ prompt, style, ratio, contextId }),
    })
  },

  /** 获取收藏列表 */
  getFavorites: (limit = 20, offset = 0) =>
    api.get('/image/favorites', { params: { limit, offset } }),

  /** 添加收藏 */
  addFavorite: (data: { imageUrl: string; prompt?: string; style?: string; ratio?: string }) =>
    api.post('/image/favorites', data),

  /** 取消收藏 */
  removeFavorite: (id: number) => api.delete(`/image/favorites/${id}`),
}

// ─── 旅游攻略 ────────────────────────────────────────────────

export const travelApi = {
  /** SSE 流式攻略生成 */
  streamGenerate: (destination: string, days: number, preferences: string) => {
    const token = localStorage.getItem('token')
    return fetch(`${API_BASE}/travel`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({ destination, days, preferences }),
    })
  },

  /** 导出攻略 */
  exportTravel: (contextId: string, format: 'pdf' | 'image') =>
    api.post('/travel/export', { contextId, format }, { responseType: 'blob' }),
}

// ─── 分享 ────────────────────────────────────────────────────

export const shareApi = {
  /** 创建分享 */
  create: (data: { type: 'travel' | 'image'; contentId: string; expiresInHours?: number }) =>
    api.post('/share', data),

  /** 获取分享内容（无需认证） */
  getContent: (token: string) => api.get(`/share/${token}`),

  /** 取消分享 */
  cancel: (token: string) => api.delete(`/share/${token}`),

  /** 我的分享列表 */
  getMine: () => api.get('/share/mine/all'),
}

// ─── 通用下载 Blob ───────────────────────────────────────────

export function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

export default api