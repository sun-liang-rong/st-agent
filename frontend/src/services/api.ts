import axios from 'axios'

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
  (error) => Promise.reject(error)
)

export interface SessionItem {
  sessionId: string
  sessionType: 'chat' | 'image'
  title: string
  summary: string
  updatedAt: string
}

export const apiService = {
  chatStream(
    message: string,
    contextId: string | undefined,
    onToken: (token: string) => void,
    onDone: (contextId: string) => void,
    onError: (error: string) => void,
  ): void {
    const token = localStorage.getItem('access_token')
    const body = JSON.stringify({ message, contextId })

    fetch('/api/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body,
    })
      .then(async (response) => {
        if (!response.ok) {
          onError(`HTTP ${response.status}`)
          return
        }

        const reader = response.body!.getReader()
        const decoder = new TextDecoder()
        let buffer = ''
        let currentEvent = ''

        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split('\n')
          buffer = lines.pop() || ''

          for (const line of lines) {
            if (line.startsWith('event: ')) {
              currentEvent = line.slice(7).trim()
            } else if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6))
                if (currentEvent === 'token' && data.content) {
                  onToken(data.content)
                } else if (currentEvent === 'done' && data.contextId) {
                  onDone(data.contextId)
                } else if (currentEvent === 'error' && data.message) {
                  onError(data.message)
                }
              } catch {
                // ignore parse errors
              }
            }
          }
        }
      })
      .catch((e) => onError(e.message))
  },

  chat(message: string, contextId?: string): Promise<{ reply: string; contextId: string }> {
    return api.post('/chat', { message, contextId })
  },

  getSessions(): Promise<SessionItem[]> {
    return api.get('/chat/sessions')
  },

  getSessionMessages(sessionId: string) {
    return api.get(`/chat/sessions/${sessionId}`)
  },

  generateImage(prompt: string, contextId?: string): Promise<{ imageUrl: string; contextId: string }> {
    return api.post('/image/generate', { prompt, contextId })
  },

  getChatHistory() {
    return api.get('/chat/history')
  },

  getChatHistoryDetail(id: string) {
    return api.get(`/chat/history/${id}`)
  },

  deleteChatHistory(id: string) {
    return api.delete(`/chat/history/${id}`)
  },

  getHistory() {
    return api.get('/history')
  },

  deleteHistory(id: string) {
    return api.delete(`/history/${id}`)
  },
}

export default api
