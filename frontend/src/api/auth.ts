/**
 * @module api/auth
 * @description Authentication API endpoints for registration, login, token
 * refresh, and user profile management.
 */

import client from './client'
import type { LoginRequest, RegisterRequest, TokenResponse, User, UserUpdateRequest } from '@/types/user'

/** Authentication API methods. */
export const authApi = {
  /**
   * Register a new user account.
   *
   * @param data - Registration payload (username, email, password, optional display name).
   * @returns Token response containing access/refresh tokens and the created user.
   *
   * @example
   * ```ts
   * const tokens = await authApi.register({
   *   username: 'alice',
   *   email: 'alice@example.com',
   *   password: 's3cret',
   * })
   * ```
   */
  register(data: RegisterRequest): Promise<TokenResponse> {
    return client.post('/auth/register', data).then((r) => r.data)
  },

  /**
   * Authenticate an existing user.
   *
   * @param data - Login payload (email and password).
   * @returns Token response containing access/refresh tokens and the user.
   */
  login(data: LoginRequest): Promise<TokenResponse> {
    return client.post('/auth/login', data).then((r) => r.data)
  },

  /**
   * Refresh the access token using a valid refresh token.
   *
   * @param refreshToken - The current refresh token string.
   * @returns New access and refresh token pair.
   */
  refresh(refreshToken: string): Promise<{ access_token: string; refresh_token: string }> {
    return client.post('/auth/refresh', { refresh_token: refreshToken }).then((r) => r.data)
  },

  /**
   * Fetch the currently authenticated user's profile.
   *
   * @returns The authenticated user.
   */
  getMe(): Promise<User> {
    return client.get('/auth/me').then((r) => r.data)
  },

  /**
   * Update the currently authenticated user's profile.
   *
   * @param data - Fields to update (display name, avatar URL).
   * @returns The updated user.
   */
  updateMe(data: UserUpdateRequest): Promise<User> {
    return client.put('/auth/me', data).then((r) => r.data)
  },
}
