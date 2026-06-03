import client from './client'
import type { Note } from '@/types/note'
import type { PaginatedResponse } from '@/types/common'

export const searchApi = {
  search(params: { q: string; type?: string; page?: number; size?: number }): Promise<PaginatedResponse<Note>> {
    return client.get('/search', { params }).then((r) => r.data)
  },
}
