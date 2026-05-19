import axios from 'axios'
import type { UploadResponse, GenerateRequest, GenerateResponse, TaskStatusResponse, PreviewResponse, SuggestResponse, DashboardSpec } from '@/types'

// 创建 axios 实例
const api = axios.create({
  baseURL: '/api',
  timeout: 120000, // 2分钟超时，因为AI生成可能需要较长时间
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// API 服务
export const apiService = {
  // 上传文件
  uploadFile(file: File): Promise<UploadResponse> {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 生成报表
  generateReport(request: GenerateRequest): Promise<GenerateResponse> {
    return api.post('/generate', request)
  },

  // 预览文件数据
  getFilePreview(fileId: string, rows: number = 50): Promise<PreviewResponse> {
    return api.get(`/upload/${fileId}/preview`, { params: { rows } })
  },

  // 获取 AI 建议的分析提示词
  suggestPrompt(fileId: string): Promise<SuggestResponse> {
    return api.get(`/upload/${fileId}/suggest`)
  },

  confirmDashboard(taskId: string, dashboardSpec: DashboardSpec): Promise<any> {
    return api.post(`/generate/${taskId}/confirm`, { dashboardSpec })
  },

  // 查询任务状态
  getTaskStatus(taskId: string): Promise<TaskStatusResponse> {
    return api.get(`/task/${taskId}`)
  },

  // 获取任务结果
  getTaskResult(taskId: string): Promise<TaskStatusResponse> {
    return api.get(`/task/${taskId}/result`)
  },

  // AI 聊天
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

  // 获取历史记录
  getHistory() {
    return api.get('/history')
  },

  // 获取历史记录详情
  getHistoryDetail(id: string) {
    return api.get(`/history/${id}`)
  },

  // 删除历史记录
  deleteHistory(id: string) {
    return api.delete(`/history/${id}`)
  },

  // 收藏报表
  collectReport(reportId: string) {
    return api.post(`/collect/${reportId}`)
  },

  // 取消收藏
  uncollectReport(reportId: string) {
    return api.delete(`/collect/${reportId}`)
  },

  // 获取收藏列表
  getCollections() {
    return api.get('/collections')
  },

  // 获取用户设置
  getSettings() {
    return api.get('/settings')
  },

  // 更新用户设置
  updateSettings(settings: any) {
    return api.put('/settings', settings)
  }
}

export default api
