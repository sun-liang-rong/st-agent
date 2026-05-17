import { defineStore } from 'pinia'
import { authApi, type RegisterRequest, type UserResponse } from '@/services/auth'

interface AuthState {
  user: UserResponse | null
  isAuthenticated: boolean
  token: string | null
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null,
    isAuthenticated: false,
    token: null
  }),

  getters: {
    currentUser: (state) => state.user,
    isLoggedIn: (state) => state.isAuthenticated
  },

  actions: {
    async login(username: string, password: string) {
      try {
        const response = await authApi.login({ username, password })
        
        this.token = response.access_token
        this.isAuthenticated = true
        
        localStorage.setItem('access_token', response.access_token)
        
        const userResponse = await authApi.getCurrentUser()
        this.user = userResponse
        localStorage.setItem('user', JSON.stringify(userResponse))
        
        return response
      } catch (error) {
        console.error('登录失败:', error)
        throw error
      }
    },

    async register(data: RegisterRequest) {
      try {
        const response = await authApi.register(data)
        return response
      } catch (error) {
        console.error('注册失败:', error)
        throw error
      }
    },

    async logout() {
      this.user = null
      this.token = null
      this.isAuthenticated = false
      
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
    },

    async checkAuth() {
      const token = localStorage.getItem('access_token')
      const userStr = localStorage.getItem('user')
      
      if (token && userStr) {
        try {
          this.token = token
          this.isAuthenticated = true
          this.user = JSON.parse(userStr)
          
          const userResponse = await authApi.getCurrentUser()
          this.user = userResponse
          localStorage.setItem('user', JSON.stringify(userResponse))
          
          return true
        } catch (error) {
          console.error('验证认证失败:', error)
          await this.logout()
          return false
        }
      }
      
      return false
    },

    setUser(user: UserResponse) {
      this.user = user
      localStorage.setItem('user', JSON.stringify(user))
    }
  }
})
