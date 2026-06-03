import client from './client'
import type { LoginRequest, RegisterRequest, TokenResponse, User, UserUpdateRequest } from '@/types/user'

export const authApi = {
  register(data: RegisterRequest): Promise<TokenResponse> {
    return client.post('/auth/register', data).then((r) => r.data)
  },

  login(data: LoginRequest): Promise<TokenResponse> {
    return client.post('/auth/login', data).then((r) => r.data)
  },

  refresh(refreshToken: string): Promise<{ access_token: string; refresh_token: string }> {
    return client.post('/auth/refresh', { refresh_token: refreshToken }).then((r) => r.data)
  },

  getMe(): Promise<User> {
    return client.get('/auth/me').then((r) => r.data)
  },

  updateMe(data: UserUpdateRequest): Promise<User> {
    return client.put('/auth/me', data).then((r) => r.data)
  },
}
