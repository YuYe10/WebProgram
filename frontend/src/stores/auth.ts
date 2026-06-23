/**
 * @module stores/auth
 * @description Pinia authentication store. Manages user identity, JWT tokens,
 * and login/register/logout flows. Tokens are persisted to localStorage and
 * the store auto-fetches the user profile on initialisation when a token exists.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import type { User, LoginRequest, RegisterRequest } from '@/types/user'
import router from '@/router'

export const useAuthStore = defineStore('auth', () => {
  // ── State ──────────────────────────────────────────────────────────────────

  /** Currently authenticated user, or `null` when logged out. */
  const user = ref<User | null>(null)

  /** Current JWT access token (also persisted in localStorage). */
  const accessToken = ref<string | null>(localStorage.getItem('access_token'))

  /** Current JWT refresh token (also persisted in localStorage). */
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))

  /** Whether an auth request (login/register) is in progress. */
  const isLoading = ref(false)

  /** Last authentication error message, or `null` when no error. */
  const error = ref<string | null>(null)

  // ── Getters ────────────────────────────────────────────────────────────────

  /** `true` when an access token is present (does not guarantee it is still valid). */
  const isAuthenticated = computed(() => !!accessToken.value)

  // ── Actions ────────────────────────────────────────────────────────────────

  /**
   * Persist access and refresh tokens to both reactive state and localStorage.
   *
   * @param access  - New access token.
   * @param refresh - New refresh token.
   */
  function setTokens(access: string, refresh: string) {
    accessToken.value = access
    refreshToken.value = refresh
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
  }

  /**
   * Remove tokens from reactive state and localStorage.
   */
  function clearTokens() {
    accessToken.value = null
    refreshToken.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  /**
   * Authenticate with email and password.
   * On success, stores tokens, sets the user, and navigates to the dashboard.
   *
   * @param data - Login credentials (email, password).
   * @throws Re-throws the API error after setting {@link error}.
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
   * On success, stores tokens, sets the user, and navigates to the dashboard.
   *
   * @param data - Registration payload (username, email, password, optional display name).
   * @throws Re-throws the API error after setting {@link error}.
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
   * If the request fails (e.g. expired token), the user is logged out.
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
   */
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
