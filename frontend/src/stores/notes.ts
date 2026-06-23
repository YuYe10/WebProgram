/**
 * @module stores/notes
 * @description Pinia store for note management. Handles fetching, creating,
 * updating, deleting, pinning, and archiving notes, as well as tracking the
 * currently active note.
 * Pinia笔记管理状态。处理笔记的获取、创建、更新、删除、置顶和归档，以及跟踪当前活动的笔记。
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'
import { notesApi } from '@/api/notes'
import type { Note, NoteCreateRequest, NoteUpdateRequest } from '@/types/note'

export const useNotesStore = defineStore('notes', () => {
  // ── State ──────────────────────────────────────────────────────────────────
  // ── 状态 ──────────────────────────────────────────────────────────────────

  /** List of notes currently loaded for the active view.
   * 当前为活动视图加载的笔记列表。
   */
  const notes = ref<Note[]>([])

  /** The note currently open in the editor, or `null`.
   * 当前在编辑器中打开的笔记，或`null`。
   */
  const activeNote = ref<Note | null>(null)

  /** Whether a note-fetching request is in progress.
   * 笔记获取请求是否正在进行中。
   */
  const isLoading = ref(false)

  /** Total number of notes matching the last query (for pagination).
   * 匹配最后一次查询的笔记总数（用于分页）。
   */
  const total = ref(0)

  /** Last error message from a note operation, or `null`.
   * 笔记操作的最后错误消息，或`null`。
   */
  const error = ref<string | null>(null)

  // ── Actions ────────────────────────────────────────────────────────────────
  // ── 操作 ────────────────────────────────────────────────────────────────

  /**
   * Fetch notes belonging to a specific notebook.
   * 获取属于特定笔记本的笔记。
   *
   * @param notebookId - Parent notebook ID.
   *                     父笔记本ID。
   * @param params     - Optional filters and pagination.
   *                     可选过滤器和分页。
   */
  async function fetchNotes(notebookId: string, params?: {
    pinned?: boolean
    archived?: boolean
    tag_id?: string
    page?: number
    size?: number
  }) {
    isLoading.value = true
    error.value = null
    try {
      const response = await notesApi.getAll(notebookId, params)
      notes.value = response.items
      total.value = response.total
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to load notes'
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Fetch a single note by ID and set it as the active note.
   * 根据ID获取单个笔记并将其设置为活动笔记。
   *
   * @param id - The note's unique identifier.
   *             笔记的唯一标识符。
   * @returns The fetched note.
   *          获取的笔记。
   */
  async function fetchNote(id: string): Promise<Note> {
    const note = await notesApi.getById(id)
    activeNote.value = note
    return note
  }

  /**
   * Create a new note inside a notebook.
   * 在笔记本内创建新笔记。
   * The new note is prepended to the local list.
   * 新笔记被添加到本地列表的开头。
   *
   * @param notebookId - Parent notebook ID.
   *                     父笔记本ID。
   * @param data       - Creation payload.
   *                     创建负载。
   * @returns The newly created note.
   *          新创建的笔记。
   */
  async function createNote(notebookId: string, data: NoteCreateRequest): Promise<Note> {
    const note = await notesApi.create(notebookId, data)
    notes.value.unshift(note)
    return note
  }

  /**
   * Update an existing note.
   * 更新现有笔记。
   * Both the list entry and the active note are refreshed on success.
   * 成功时刷新列表条目和活动笔记。
   *
   * @param id   - The note's unique identifier.
   *               笔记的唯一标识符。
   * @param data - Fields to update.
   *               要更新的字段。
   * @returns The updated note.
   *          更新后的笔记。
   */
  async function updateNote(id: string, data: NoteUpdateRequest): Promise<Note> {
    const note = await notesApi.update(id, data)
    const index = notes.value.findIndex((n) => n.id === id)
    if (index !== -1) notes.value[index] = note
    if (activeNote.value?.id === id) activeNote.value = note
    return note
  }

  /**
   * Delete a note permanently.
   * 永久删除笔记。
   * Removes it from the local list and clears the active note if it was selected.
   * 从本地列表中移除它，如果它被选中则清除活动笔记。
   *
   * @param id - The note's unique identifier.
   *             笔记的唯一标识符。
   */
  async function deleteNote(id: string) {
    await notesApi.delete(id)
    notes.value = notes.value.filter((n) => n.id !== id)
    if (activeNote.value?.id === id) activeNote.value = null
  }

  /**
   * Toggle the pinned status of a note.
   * 切换笔记的置顶状态。
   *
   * @param id        - The note's unique identifier.
   *                    笔记的唯一标识符。
   * @param isPinned  - `true` to pin, `false` to unpin.
   *                    `true`表示置顶，`false`表示取消置顶。
   */
  async function togglePin(id: string, isPinned: boolean) {
    const note = await notesApi.pin(id, isPinned)
    const index = notes.value.findIndex((n) => n.id === id)
    if (index !== -1) notes.value[index] = note
    if (activeNote.value?.id === id) activeNote.value = note
  }

  /**
   * Toggle the archived status of a note.
   * 切换笔记的归档状态。
   *
   * @param id          - The note's unique identifier.
   *                      笔记的唯一标识符。
   * @param isArchived  - `true` to archive, `false` to unarchive.
   *                      `true`表示归档，`false`表示取消归档。
   */
  async function toggleArchive(id: string, isArchived: boolean) {
    const note = await notesApi.archive(id, isArchived)
    const index = notes.value.findIndex((n) => n.id === id)
    if (index !== -1) notes.value[index] = note
    if (activeNote.value?.id === id) activeNote.value = note
  }

  /**
   * Set the currently active note.
   * 设置当前活动的笔记。
   *
   * @param note - The note to make active, or `null` to clear.
   *               要设为活动的笔记，或`null`来清除。
   */
  function setActiveNote(note: Note | null) {
    activeNote.value = note
  }

  return {
    notes,
    activeNote,
    isLoading,
    total,
    error,
    fetchNotes,
    fetchNote,
    createNote,
    updateNote,
    deleteNote,
    togglePin,
    toggleArchive,
    setActiveNote,
  }
})
