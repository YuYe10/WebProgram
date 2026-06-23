/**
 * @module stores/auth
 * @description Pinia authentication store. Manages user identity, JWT tokens,
 * and login/register/logout flows. Tokens are persisted to localStorage and
 * the store auto-fetches the user profile on initialisation when a token exists.
 * Pinia认证状态管理。管理用户身份、JWT令牌和登录/注册/登出流程。
 * 令牌持久化到localStorage，当令牌存在时，store会在初始化时自动获取用户资料。
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import type { User, LoginRequest, RegisterRequest } from '@/types/user'
import router from '@/router'

export const useAuthStore = defineStore('auth', () => {
  // ── State ──────────────────────────────────────────────────────────────────
  // ── 状态 ──────────────────────────────────────────────────────────────────

  /** Currently authenticated user, or `null` when logged out.
   * 当前已认证的用户，登出时为`null`。
   */
  const user = ref<User | null>(null)

  /** Current JWT access token (also persisted in localStorage).
   * 当前的JWT访问令牌（也持久化在localStorage中）。
   */
  const accessToken = ref<string | null>(localStorage.getItem('access_token'))

  /** Current JWT refresh token (also persisted in localStorage).
   * 当前的JWT刷新令牌（也持久化在localStorage中）。
   */
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))

  /** Whether an auth request (login/register) is in progress.
   * 认证请求（登录/注册）是否正在进行中。
   */
  const isLoading = ref(false)

  /** Last authentication error message, or `null` when no error.
   * 最后一次认证错误消息，没有错误时为`null`。
   */
  const error = ref<string | null>(null)

  // ── Getters ────────────────────────────────────────────────────────────────
  // ── 计算属性 ────────────────────────────────────────────────────────────────

  /** `true` when an access token is present (does not guarantee it is still valid).
   * 当存在访问令牌时为`true`（不保证令牌仍然有效）。
   */
  const isAuthenticated = computed(() => !!accessToken.value)

  // ── Actions ────────────────────────────────────────────────────────────────
  // ── 操作 ────────────────────────────────────────────────────────────────

  /**
   * Persist access and refresh tokens to both reactive state and localStorage.
   * 将访问令牌和刷新令牌持久化到响应式状态和localStorage中。
   *
   * @param access  - New access token.
   *                  新的访问令牌。
   * @param refresh - New refresh token.
   *                  新的刷新令牌。
   */
  function setTokens(access: string, refresh: string) {
    accessToken.value = access
    refreshToken.value = refresh
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
  }

  /**
   * Remove tokens from reactive state and localStorage.
   * 从响应式状态和localStorage中移除令牌。
   */
  function clearTokens() {
    accessToken.value = null
    refreshToken.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  /**
   * Authenticate with email and password.
   * 使用邮箱和密码进行认证。
   * On success, stores tokens, sets the user, and navigates to the dashboard.
   * 成功时，存储令牌，设置用户，并导航到仪表板。
   *
   * @param data - Login credentials (email, password).
   *               登录凭证（邮箱、密码）。
   * @throws Re-throws the API error after setting {@link error}.
   *         设置错误后重新抛出API错误。
   */
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

  /**
   * Register a new account.
   * 注册新账户。
   * On success, stores tokens, sets the user, and navigates to the dashboard.
   * 成功时，存储令牌，设置用户，并导航到仪表板。
   *
   * @param data - Registration payload (username, email, password, optional display name).
   *               注册负载（用户名、邮箱、密码、可选显示名称）。
   * @throws Re-throws the API error after setting {@link error}.
   *         设置错误后重新抛出API错误。
   */
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

  /**
   * Fetch the current user's profile from the API.
   * 从API获取当前用户的资料。
   * If the request fails (e.g. expired token), the user is logged out.
   * 如果请求失败（例如令牌过期），用户将被登出。
   */
  async function fetchUser() {
    if (!accessToken.value) return
    try {
      user.value = await authApi.getMe()
    } catch {
      logout()
    }
  }

  /**
   * Clear all auth state and redirect to the login page.
   * 清除所有认证状态并重定向到登录页面。
   */
  function logout() {
    clearTokens()
    user.value = null
    router.push('/auth/login')
  }

  // Initialize: fetch user if token exists
  // 初始化：如果存在令牌则获取用户
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
