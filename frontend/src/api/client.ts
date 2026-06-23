/**
 * @module api/client
 * @description Axios HTTP client instance with JWT authentication interceptors.
 * Provides automatic access-token injection on requests and transparent
 * token-refresh with request queuing on 401 responses.
 */

import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

/** Pre-configured Axios instance pointing at the backend API. */
const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// ── Request interceptor: attach access token ────────────────────────────────
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// ── Response interceptor: handle 401 with token refresh ─────────────────────

/**
 * Whether a token refresh is currently in flight.
 * Prevents multiple concurrent refresh requests.
 */
let isRefreshing = false

/**
 * Queue of requests that failed while a refresh was in progress.
 * Each entry resolves/rejects once the refresh attempt completes.
 */
let failedQueue: Array<{
  resolve: (token: string) => void
  reject: (error: any) => void
}> = []

/**
 * Resolves or rejects all queued requests after a refresh attempt.
 *
 * @param error  - If non-null, the refresh failed and every queued request is rejected.
 * @param token  - If non-null, the new access token to retry queued requests with.
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
