import client from './client'
import type { Notebook, NotebookCreateRequest, NotebookUpdateRequest } from '@/types/notebook'
import type { PaginatedResponse } from '@/types/common'

export const notebooksApi = {
  getAll(params?: { archived?: boolean; page?: number; size?: number }): Promise<PaginatedResponse<Notebook>> {
    return client.get('/notebooks', { params }).then((r) => r.data)
  },

  getById(id: string): Promise<Notebook> {
    return client.get(`/notebooks/${id}`).then((r) => r.data)
  },

  create(data: NotebookCreateRequest): Promise<Notebook> {
    return client.post('/notebooks', data).then((r) => r.data)
  },

  update(id: string, data: NotebookUpdateRequest): Promise<Notebook> {
    return client.put(`/notebooks/${id}`, data).then((r) => r.data)
  },

  delete(id: string): Promise<void> {
    return client.delete(`/notebooks/${id}`)
  },
}
