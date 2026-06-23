/**
 * @module api/client
 * @description Axios HTTP client instance with JWT authentication interceptors.
 * Provides automatic access-token injection on requests and transparent
 * token-refresh with request queuing on 401 responses.
 * 带有JWT认证拦截器的Axios HTTP客户端实例。
 * 提供请求时自动注入访问令牌，并在401响应时透明地刷新令牌并排队请求。
 */

import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

/** Pre-configured Axios instance pointing at the backend API.
 * 指向后端API的预配置Axios实例。
 */
const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// ── Request interceptor: attach access token ────────────────────────────────
// ── 请求拦截器：附加访问令牌 ────────────────────────────────
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// ── Response interceptor: handle 401 with token refresh ─────────────────────
// ── 响应拦截器：处理401并刷新令牌 ─────────────────────

/**
 * Whether a token refresh is currently in flight.
 * 是否正在刷新令牌。
 * Prevents multiple concurrent refresh requests.
 * 防止多个并发的刷新请求。
 */
let isRefreshing = false

/**
 * Queue of requests that failed while a refresh was in progress.
 * 刷新过程中失败的请求队列。
 * Each entry resolves/rejects once the refresh attempt completes.
 * 刷新尝试完成后，每个条目都会被解析或拒绝。
 */
let failedQueue: Array<{
  resolve: (token: string) => void
  reject: (error: any) => void
}> = []

/**
 * Resolves or rejects all queued requests after a refresh attempt.
 * 刷新尝试后解析或拒绝所有排队的请求。
 *
 * @param error  - If non-null, the refresh failed and every queued request is rejected.
 *                 如果非空，刷新失败，所有排队请求都被拒绝。
 * @param token  - If non-null, the new access token to retry queued requests with.
 *                 如果非空，用于重试排队请求的新访问令牌。
 */
const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token!)
    }
  })
  failedQueue = []
}

client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      // If a refresh is already in flight, queue this request so it can be
      // retried once the new token is available.
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            return client(originalRequest)
          })
          .catch((err) => Promise.reject(err))
      }

      originalRequest._retry = true
      isRefreshing = true

      const refreshToken = localStorage.getItem('refresh_token')
      if (!refreshToken) {
        isRefreshing = false
        const authStore = useAuthStore()
        authStore.logout()
        return Promise.reject(error)
      }

      try {
        const { data } = await axios.post(
          `${client.defaults.baseURL}/auth/refresh`,
          { refresh_token: refreshToken }
        )
        // Sync tokens to localStorage
        localStorage.setItem('access_token', data.access_token)
        localStorage.setItem('refresh_token', data.refresh_token)
        // Sync tokens to Pinia auth store
        const authStore = useAuthStore()
        authStore.accessToken = data.access_token
        authStore.refreshToken = data.refresh_token
        // Resolve all queued requests with the new token
        processQueue(null, data.access_token)
        originalRequest.headers.Authorization = `Bearer ${data.access_token}`
        return client(originalRequest)
      } catch (refreshError) {
        // Reject all queued requests — the refresh itself failed
        processQueue(refreshError, null)
        const authStore = useAuthStore()
        authStore.logout()
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  }
)

export default client
