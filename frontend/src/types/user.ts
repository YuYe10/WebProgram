export interface User {
  id: string
  username: string
  email: string
  display_name: string | null
  avatar_url: string | null
  created_at: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
  display_name?: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user: User
}

export interface UserUpdateRequest {
  display_name?: string
  avatar_url?: string
}
