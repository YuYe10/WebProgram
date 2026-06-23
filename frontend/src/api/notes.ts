/**
 * @module api/notes
 * @description Note CRUD and action API endpoints. Notes belong to notebooks
 * and support pinning, archiving, and tag attachment/detachment.
 * 笔记CRUD和操作API端点。笔记属于笔记本，支持置顶、归档和标签的添加/移除。
 */

import client from './client'
import type { Note, NoteCreateRequest, NoteUpdateRequest } from '@/types/note'
import type { PaginatedResponse } from '@/types/common'

/** Note API methods.
 * 笔记API方法。
 */
export const notesApi = {
  /**
   * List all notes within a specific notebook.
   * 列出特定笔记本内的所有笔记。
   *
   * @param notebookId - Parent notebook ID.
   *                     父笔记本ID。
   * @param params     - Optional query parameters.
   *                     可选查询参数。
   * @param params.pinned   - Filter by pinned status.
   *                          按置顶状态过滤。
   * @param params.archived - Filter by archived status.
   *                          按归档状态过滤。
   * @param params.tag_id   - Filter by tag ID.
   *                          按标签ID过滤。
   * @param params.page     - Page number (1-based).
   *                          页码（从1开始）。
   * @param params.size     - Items per page.
   *                          每页项目数。
   * @returns Paginated list of notes.
   *          分页的笔记列表。
   */
  getAll(
    notebookId: string,
    params?: { pinned?: boolean; archived?: boolean; tag_id?: string; page?: number; size?: number }
  ): Promise<PaginatedResponse<Note>> {
    return client.get(`/notebooks/${notebookId}/notes`, { params }).then((r) => r.data)
  },

  /**
   * Fetch a single note by its ID.
   * 根据ID获取单个笔记。
   *
   * @param id - The note's unique identifier.
   *             笔记的唯一标识符。
   * @returns The requested note.
   *          请求的笔记。
   */
  getById(id: string): Promise<Note> {
    return client.get(`/notes/${id}`).then((r) => r.data)
  },

  /**
   * Create a new note inside a notebook.
   * 在笔记本内创建新笔记。
   *
   * @param notebookId - Parent notebook ID.
   *                     父笔记本ID。
   * @param data       - Creation payload (title, optional content and tag IDs).
   *                     创建负载（标题、可选内容和标签ID）。
   * @returns The newly created note.
   *          新创建的笔记。
   */
  create(notebookId: string, data: NoteCreateRequest): Promise<Note> {
    return client.post(`/notebooks/${notebookId}/notes`, data).then((r) => r.data)
  },

  /**
   * Update an existing note.
   * 更新现有笔记。
   *
   * @param id   - The note's unique identifier.
   *               笔记的唯一标识符。
   * @param data - Fields to update.
   *               要更新的字段。
   * @returns The updated note.
   *          更新后的笔记。
   */
  update(id: string, data: NoteUpdateRequest): Promise<Note> {
    return client.put(`/notes/${id}`, data).then((r) => r.data)
  },

  /**
   * Delete a note permanently.
   * 永久删除笔记。
   *
   * @param id - The note's unique identifier.
   *             笔记的唯一标识符。
   * @returns Resolves when deletion is complete.
   *          删除完成时解析。
   */
  delete(id: string): Promise<void> {
    return client.delete(`/notes/${id}`)
  },

  /**
   * Toggle the pinned status of a note.
   * 切换笔记的置顶状态。
   *
   * @param id        - The note's unique identifier.
   *                    笔记的唯一标识符。
   * @param isPinned  - `true` to pin, `false` to unpin.
   *                    `true`表示置顶，`false`表示取消置顶。
   * @returns The updated note.
   *          更新后的笔记。
   */
  pin(id: string, isPinned: boolean): Promise<Note> {
    return client.patch(`/notes/${id}/pin`, { is_pinned: isPinned }).then((r) => r.data)
  },

  /**
   * List all notes across every notebook.
   * 列出所有笔记本中的所有笔记。
   *
   * @param params - Optional query parameters.
   *                 可选查询参数。
   * @param params.page   - Page number (1-based).
   *                        页码（从1开始）。
   * @param params.size   - Items per page.
   *                        每页项目数。
   * @param params.tag_id - Filter by tag ID.
   *                        按标签ID过滤。
   * @returns Paginated list of notes.
   *          分页的笔记列表。
   */
  getAllNotes(params?: { page?: number; size?: number; tag_id?: string }): Promise<PaginatedResponse<Note>> {
    return client.get('/notes', { params }).then((r) => r.data)
  },

  /**
   * List all archived notes across every notebook.
   * 列出所有笔记本中的所有已归档笔记。
   *
   * @param params - Optional query parameters.
   *                 可选查询参数。
   * @param params.page - Page number (1-based).
   *                      页码（从1开始）。
   * @param params.size - Items per page.
   *                      每页项目数。
   * @returns Paginated list of archived notes.
   *          分页的已归档笔记列表。
   */
  getArchivedNotes(params?: { page?: number; size?: number }): Promise<PaginatedResponse<Note>> {
    return client.get('/notes/archived', { params }).then((r) => r.data)
  },

  /**
   * Toggle the archived status of a note.
   * 切换笔记的归档状态。
   *
   * @param id          - The note's unique identifier.
   *                      笔记的唯一标识符。
   * @param isArchived  - `true` to archive, `false` to unarchive.
   *                      `true`表示归档，`false`表示取消归档。
   * @returns The updated note.
   *          更新后的笔记。
   */
  archive(id: string, isArchived: boolean): Promise<Note> {
    return client.patch(`/notes/${id}/archive`, { is_archived: isArchived }).then((r) => r.data)
  },

  /**
   * Attach a tag to a note.
   * 为笔记添加标签。
   *
   * @param noteId - The note's unique identifier.
   *                 笔记的唯一标识符。
   * @param tagId  - The tag's unique identifier.
   *                 标签的唯一标识符。
   * @returns The updated note with the new tag attached.
   *          添加了新标签的更新后的笔记。
   */
  attachTag(noteId: string, tagId: string): Promise<Note> {
    return client.post(`/notes/${noteId}/tags`, { tag_id: tagId }).then((r) => r.data)
  },

  /**
   * Detach a tag from a note.
   * 从笔记移除标签。
   *
   * @param noteId - The note's unique identifier.
   *                 笔记的唯一标识符。
   * @param tagId  - The tag's unique identifier.
   *                 标签的唯一标识符。
   * @returns The updated note with the tag removed.
   *          移除了标签的更新后的笔记。
   */
  detachTag(noteId: string, tagId: string): Promise<Note> {
    return client.delete(`/notes/${noteId}/tags/${tagId}`).then((r) => r.data)
  },
}
