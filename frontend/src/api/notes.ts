/**
 * @module api/notes
 * @description Note CRUD and action API endpoints. Notes belong to notebooks
 * and support pinning, archiving, and tag attachment/detachment.
 */

import client from './client'
import type { Note, NoteCreateRequest, NoteUpdateRequest } from '@/types/note'
import type { PaginatedResponse } from '@/types/common'

/** Note API methods. */
export const notesApi = {
  /**
   * List all notes within a specific notebook.
   *
   * @param notebookId - Parent notebook ID.
   * @param params     - Optional query parameters.
   * @param params.pinned   - Filter by pinned status.
   * @param params.archived - Filter by archived status.
   * @param params.tag_id   - Filter by tag ID.
   * @param params.page     - Page number (1-based).
   * @param params.size     - Items per page.
   * @returns Paginated list of notes.
   */
  getAll(
    notebookId: string,
    params?: { pinned?: boolean; archived?: boolean; tag_id?: string; page?: number; size?: number }
  ): Promise<PaginatedResponse<Note>> {
    return client.get(`/notebooks/${notebookId}/notes`, { params }).then((r) => r.data)
  },

  /**
   * Fetch a single note by its ID.
   *
   * @param id - The note's unique identifier.
   * @returns The requested note.
   */
  getById(id: string): Promise<Note> {
    return client.get(`/notes/${id}`).then((r) => r.data)
  },

  /**
   * Create a new note inside a notebook.
   *
   * @param notebookId - Parent notebook ID.
   * @param data       - Creation payload (title, optional content and tag IDs).
   * @returns The newly created note.
   */
  create(notebookId: string, data: NoteCreateRequest): Promise<Note> {
    return client.post(`/notebooks/${notebookId}/notes`, data).then((r) => r.data)
  },

  /**
   * Update an existing note.
   *
   * @param id   - The note's unique identifier.
   * @param data - Fields to update.
   * @returns The updated note.
   */
  update(id: string, data: NoteUpdateRequest): Promise<Note> {
    return client.put(`/notes/${id}`, data).then((r) => r.data)
  },

  /**
   * Delete a note permanently.
   *
   * @param id - The note's unique identifier.
   * @returns Resolves when deletion is complete.
   */
  delete(id: string): Promise<void> {
    return client.delete(`/notes/${id}`)
  },

  /**
   * Toggle the pinned status of a note.
   *
   * @param id        - The note's unique identifier.
   * @param isPinned  - `true` to pin, `false` to unpin.
   * @returns The updated note.
   */
  pin(id: string, isPinned: boolean): Promise<Note> {
    return client.patch(`/notes/${id}/pin`, { is_pinned: isPinned }).then((r) => r.data)
  },

  /**
   * List all notes across every notebook.
   *
   * @param params - Optional query parameters.
   * @param params.page   - Page number (1-based).
   * @param params.size   - Items per page.
   * @param params.tag_id - Filter by tag ID.
   * @returns Paginated list of notes.
   */
  getAllNotes(params?: { page?: number; size?: number; tag_id?: string }): Promise<PaginatedResponse<Note>> {
    return client.get('/notes', { params }).then((r) => r.data)
  },

  /**
   * List all archived notes across every notebook.
   *
   * @param params - Optional query parameters.
   * @param params.page - Page number (1-based).
   * @param params.size - Items per page.
   * @returns Paginated list of archived notes.
   */
  getArchivedNotes(params?: { page?: number; size?: number }): Promise<PaginatedResponse<Note>> {
    return client.get('/notes/archived', { params }).then((r) => r.data)
  },

  /**
   * Toggle the archived status of a note.
   *
   * @param id          - The note's unique identifier.
   * @param isArchived  - `true` to archive, `false` to unarchive.
   * @returns The updated note.
   */
  archive(id: string, isArchived: boolean): Promise<Note> {
    return client.patch(`/notes/${id}/archive`, { is_archived: isArchived }).then((r) => r.data)
  },

  /**
   * Attach a tag to a note.
   *
   * @param noteId - The note's unique identifier.
   * @param tagId  - The tag's unique identifier.
   * @returns The updated note with the new tag attached.
   */
  attachTag(noteId: string, tagId: string): Promise<Note> {
    return client.post(`/notes/${noteId}/tags`, { tag_id: tagId }).then((r) => r.data)
  },

  /**
   * Detach a tag from a note.
   *
   * @param noteId - The note's unique identifier.
   * @param tagId  - The tag's unique identifier.
   * @returns The updated note with the tag removed.
   */
  detachTag(noteId: string, tagId: string): Promise<Note> {
    return client.delete(`/notes/${noteId}/tags/${tagId}`).then((r) => r.data)
  },
}
