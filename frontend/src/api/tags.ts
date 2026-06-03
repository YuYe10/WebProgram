import client from './client'
import type { Tag, TagCreateRequest, TagUpdateRequest } from '@/types/tag'
import type { PaginatedResponse } from '@/types/common'

export const tagsApi = {
  getAll(params?: { page?: number; size?: number }): Promise<PaginatedResponse<Tag>> {
    return client.get('/tags', { params }).then((r) => r.data)
  },

  create(data: TagCreateRequest): Promise<Tag> {
    return client.post('/tags', data).then((r) => r.data)
  },

  update(id: string, data: TagUpdateRequest): Promise<Tag> {
    return client.put(`/tags/${id}`, data).then((r) => r.data)
  },

  delete(id: string): Promise<void> {
    return client.delete(`/tags/${id}`)
  },
}
