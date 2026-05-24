import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export interface RegisterRequest {
  username: string
  password: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  expires_in: number
}

export interface UserResponse {
  id: number
  username: string
  email: string
  full_name?: string
  avatar_url?: string
  is_active: boolean
  created_at: string
}

export const authApi = {
  register(data: RegisterRequest): Promise<UserResponse> {
    return api.post('/auth/register', data)
  },

  login(data: LoginRequest): Promise<TokenResponse> {
    return api.post('/auth/login', data)
  },

  loginOAuth2(username: string, password: string): Promise<TokenResponse> {
    const formData = new URLSearchParams()
    formData.append('username', username)
    formData.append('password', password)
    return api.post('/auth/login/oauth2', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })
  },

  getCurrentUser(): Promise<UserResponse> {
    return api.get('/auth/me')
  },

  updateProfile(data: { full_name?: string; email?: string }): Promise<UserResponse> {
    return api.put('/auth/profile', data)
  },

  changePassword(data: { old_password: string; new_password: string }): Promise<void> {
    return api.put('/auth/password', data)
  },

  uploadAvatar(file: File): Promise<{ avatar_url: string }> {
    const fd = new FormData()
    fd.append('file', file)
    return api.post('/auth/avatar', fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}

export default api
