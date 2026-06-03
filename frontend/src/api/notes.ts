import client from './client'
import type { Note, NoteCreateRequest, NoteUpdateRequest } from '@/types/note'
import type { PaginatedResponse } from '@/types/common'

export const notesApi = {
  getAll(
    notebookId: string,
    params?: { pinned?: boolean; archived?: boolean; tag_id?: string; page?: number; size?: number }
  ): Promise<PaginatedResponse<Note>> {
    return client.get(`/notebooks/${notebookId}/notes`, { params }).then((r) => r.data)
  },

  getById(id: string): Promise<Note> {
    return client.get(`/notes/${id}`).then((r) => r.data)
  },

  create(notebookId: string, data: NoteCreateRequest): Promise<Note> {
    return client.post(`/notebooks/${notebookId}/notes`, data).then((r) => r.data)
  },

  update(id: string, data: NoteUpdateRequest): Promise<Note> {
    return client.put(`/notes/${id}`, data).then((r) => r.data)
  },

  delete(id: string): Promise<void> {
    return client.delete(`/notes/${id}`)
  },

  pin(id: string, isPinned: boolean): Promise<Note> {
    return client.patch(`/notes/${id}/pin`, { is_pinned: isPinned }).then((r) => r.data)
  },

  archive(id: string, isArchived: boolean): Promise<Note> {
    return client.patch(`/notes/${id}/archive`, { is_archived: isArchived }).then((r) => r.data)
  },

  attachTag(noteId: string, tagId: string): Promise<void> {
    return client.post(`/notes/${noteId}/tags`, { tag_id: tagId })
  },

  detachTag(noteId: string, tagId: string): Promise<void> {
    return client.delete(`/notes/${noteId}/tags/${tagId}`)
  },
}
