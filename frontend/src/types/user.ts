/**
 * @module types/user
 * @description Type definitions for user entities and authentication-related
 * request/response payloads.
 * 用户实体和认证相关请求/响应负载的类型定义。
 */

/** Represents a user returned by the API.
 * 表示API返回的用户。
 */
export interface User {
  /** Unique identifier (UUID).
   * 唯一标识符(UUID)。
   */
  id: string
  /** Unique username.
   * 唯一用户名。
   */
  username: string
  /** Unique email address.
   * 唯一电子邮件地址。
   */
  email: string
  /** Display name chosen by the user, or `null`.
   * 用户选择的显示名称，或`null`。
   */
  display_name: string | null
  /** URL of the user's avatar image, or `null`.
   * 用户头像图片的URL，或`null`。
   */
  avatar_url: string | null
  /** ISO-8601 timestamp when the account was created.
   * 账户创建时的ISO-8601时间戳。
   */
  created_at: string
}

/** Payload for the login endpoint.
 * 登录端点的负载。
 */
export interface LoginRequest {
  /** User's email address.
   * 用户的电子邮件地址。
   */
  email: string
  /** User's password.
   * 用户的密码。
   */
  password: string
}

/** Payload for the registration endpoint.
 * 注册端点的负载。
 */
export interface RegisterRequest {
  /** Desired username.
   * 期望的用户名。
   */
  username: string
  /** User's email address.
   * 用户的电子邮件地址。
   */
  email: string
  /** User's password.
   * 用户的密码。
   */
  password: string
  /** Optional display name.
   * 可选的显示名称。
   */
  display_name?: string
}

/** Response from login/register endpoints containing JWT tokens and the user.
 * 登录/注册端点的响应，包含JWT令牌和用户。
 */
export interface TokenResponse {
  /** JWT access token for API authentication.
   * 用于API认证的JWT访问令牌。
   */
  access_token: string
  /** JWT refresh token used to obtain a new access token.
   * 用于获取新访问令牌的JWT刷新令牌。
   */
  refresh_token: string
  /** Token type (always `"bearer"`).
   * 令牌类型（始终为`"bearer"`）。
   */
  token_type: string
  /** The authenticated user.
   * 已认证的用户。
   */
  user: User
}

/** Payload for updating the current user's profile. All fields are optional.
 * 更新当前用户资料的负载。所有字段都是可选的。
 */
export interface UserUpdateRequest {
  /** New display name.
   * 新的显示名称。
   */
  display_name?: string
  /** New avatar URL.
   * 新的头像URL。
   */
  avatar_url?: string
}
