/**
 * @module stores/notes
 * @description Pinia store for note management. Handles fetching, creating,
 * updating, deleting, pinning, and archiving notes, as well as tracking the
 * currently active note.
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'
import { notesApi } from '@/api/notes'
import type { Note, NoteCreateRequest, NoteUpdateRequest } from '@/types/note'

export const useNotesStore = defineStore('notes', () => {
  // ── State ──────────────────────────────────────────────────────────────────

  /** List of notes currently loaded for the active view. */
  const notes = ref<Note[]>([])

  /** The note currently open in the editor, or `null`. */
  const activeNote = ref<Note | null>(null)

  /** Whether a note-fetching request is in progress. */
  const isLoading = ref(false)

  /** Total number of notes matching the last query (for pagination). */
  const total = ref(0)

  /** Last error message from a note operation, or `null`. */
  const error = ref<string | null>(null)

  // ── Actions ────────────────────────────────────────────────────────────────

  /**
   * Fetch notes belonging to a specific notebook.
   *
   * @param notebookId - Parent notebook ID.
   * @param params     - Optional filters and pagination.
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
   *
   * @param id - The note's unique identifier.
   * @returns The fetched note.
   */
  async function fetchNote(id: string): Promise<Note> {
    const note = await notesApi.getById(id)
    activeNote.value = note
    return note
  }

  /**
   * Create a new note inside a notebook.
   * The new note is prepended to the local list.
   *
   * @param notebookId - Parent notebook ID.
   * @param data       - Creation payload.
   * @returns The newly created note.
   */
  async function createNote(notebookId: string, data: NoteCreateRequest): Promise<Note> {
    const note = await notesApi.create(notebookId, data)
    notes.value.unshift(note)
    return note
  }

  /**
   * Update an existing note.
   * Both the list entry and the active note are refreshed on success.
   *
   * @param id   - The note's unique identifier.
   * @param data - Fields to update.
   * @returns The updated note.
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
   * Removes it from the local list and clears the active note if it was selected.
   *
   * @param id - The note's unique identifier.
   */
  async function deleteNote(id: string) {
    await notesApi.delete(id)
    notes.value = notes.value.filter((n) => n.id !== id)
    if (activeNote.value?.id === id) activeNote.value = null
  }

  /**
   * Toggle the pinned status of a note.
   *
   * @param id        - The note's unique identifier.
   * @param isPinned  - `true` to pin, `false` to unpin.
   */
  async function togglePin(id: string, isPinned: boolean) {
    const note = await notesApi.pin(id, isPinned)
    const index = notes.value.findIndex((n) => n.id === id)
    if (index !== -1) notes.value[index] = note
    if (activeNote.value?.id === id) activeNote.value = note
  }

  /**
   * Toggle the archived status of a note.
   *
   * @param id          - The note's unique identifier.
   * @param isArchived  - `true` to archive, `false` to unarchive.
   */
  async function toggleArchive(id: string, isArchived: boolean) {
    const note = await notesApi.archive(id, isArchived)
    const index = notes.value.findIndex((n) => n.id === id)
    if (index !== -1) notes.value[index] = note
    if (activeNote.value?.id === id) activeNote.value = note
  }

  /**
   * Set the currently active note.
   *
   * @param note - The note to make active, or `null` to clear.
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
