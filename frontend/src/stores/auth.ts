import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import type { User, LoginRequest, RegisterRequest } from '@/types/user'
import router from '@/router'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(localStorage.getItem('access_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => !!accessToken.value)

  function setTokens(access: string, refresh: string) {
    accessToken.value = access
    refreshToken.value = refresh
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
  }

  function clearTokens() {
    accessToken.value = null
    refreshToken.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  async function login(data: LoginRequest) {
    isLoading.value = true
    error.value = null
    try {
      const response = await authApi.login(data)
      setTokens(response.access_token, response.refresh_token)
      user.value = response.user
      router.push('/')
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Login failed'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function register(data: RegisterRequest) {
    isLoading.value = true
    error.value = null
    try {
      const response = await authApi.register(data)
      setTokens(response.access_token, response.refresh_token)
      user.value = response.user
      router.push('/')
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Registration failed'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function fetchUser() {
    if (!accessToken.value) return
    try {
      user.value = await authApi.getMe()
    } catch {
      logout()
    }
  }

  function logout() {
    clearTokens()
    user.value = null
    router.push('/auth/login')
  }

  // Initialize: fetch user if token exists
  if (accessToken.value) {
    fetchUser()
  }

  return {
    user,
    accessToken,
    refreshToken,
    isLoading,
    error,
    isAuthenticated,
    login,
    register,
    fetchUser,
    logout,
  }
})
