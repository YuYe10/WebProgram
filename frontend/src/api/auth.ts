/**
 * @module api/auth
 * @description Authentication API endpoints for registration, login, token
 * refresh, and user profile management.
 * 认证API端点：注册、登录、令牌刷新和用户资料管理。
 */

import client from './client'
import type { LoginRequest, RegisterRequest, TokenResponse, User, UserUpdateRequest } from '@/types/user'

/** Authentication API methods.
 * 认证API方法。
 */
export const authApi = {
  /**
   * Register a new user account.
   * 注册新用户账户。
   *
   * @param data - Registration payload (username, email, password, optional display name).
   *               注册负载（用户名、邮箱、密码、可选显示名称）。
   * @returns Token response containing access/refresh tokens and the created user.
   *          包含访问/刷新令牌和创建的用户的令牌响应。
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
   * 认证现有用户。
   *
   * @param data - Login payload (email and password).
   *               登录负载（邮箱和密码）。
   * @returns Token response containing access/refresh tokens and the user.
   *          包含访问/刷新令牌和用户的令牌响应。
   */
  login(data: LoginRequest): Promise<TokenResponse> {
    return client.post('/auth/login', data).then((r) => r.data)
  },

  /**
   * Refresh the access token using a valid refresh token.
   * 使用有效的刷新令牌刷新访问令牌。
   *
   * @param refreshToken - The current refresh token string.
   *                       当前的刷新令牌字符串。
   * @returns New access and refresh token pair.
   *          新的访问和刷新令牌对。
   */
  refresh(refreshToken: string): Promise<{ access_token: string; refresh_token: string }> {
    return client.post('/auth/refresh', { refresh_token: refreshToken }).then((r) => r.data)
  },

  /**
   * Fetch the currently authenticated user's profile.
   * 获取当前已认证用户的资料。
   *
   * @returns The authenticated user.
   *          已认证的用户。
   */
  getMe(): Promise<User> {
    return client.get('/auth/me').then((r) => r.data)
  },

  /**
   * Update the currently authenticated user's profile.
   * 更新当前已认证用户的资料。
   *
   * @param data - Fields to update (display name, avatar URL).
   *               要更新的字段（显示名称、头像URL）。
   * @returns The updated user.
   *          更新后的用户。
   */
  updateMe(data: UserUpdateRequest): Promise<User> {
    return client.put('/auth/me', data).then((r) => r.data)
  },
}
