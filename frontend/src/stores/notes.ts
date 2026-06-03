import { defineStore } from 'pinia'
import { ref } from 'vue'
import { notesApi } from '@/api/notes'
import type { Note, NoteCreateRequest, NoteUpdateRequest } from '@/types/note'

export const useNotesStore = defineStore('notes', () => {
  const notes = ref<Note[]>([])
  const activeNote = ref<Note | null>(null)
  const isLoading = ref(false)
  const total = ref(0)
  const error = ref<string | null>(null)

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

  async function fetchNote(id: string): Promise<Note> {
    const note = await notesApi.getById(id)
    activeNote.value = note
    return note
  }

  async function createNote(notebookId: string, data: NoteCreateRequest): Promise<Note> {
    const note = await notesApi.create(notebookId, data)
    notes.value.unshift(note)
    return note
  }

  async function updateNote(id: string, data: NoteUpdateRequest): Promise<Note> {
    const note = await notesApi.update(id, data)
    const index = notes.value.findIndex((n) => n.id === id)
    if (index !== -1) notes.value[index] = note
    if (activeNote.value?.id === id) activeNote.value = note
    return note
  }

  async function deleteNote(id: string) {
    await notesApi.delete(id)
    notes.value = notes.value.filter((n) => n.id !== id)
    if (activeNote.value?.id === id) activeNote.value = null
  }

  async function togglePin(id: string, isPinned: boolean) {
    const note = await notesApi.pin(id, isPinned)
    const index = notes.value.findIndex((n) => n.id === id)
    if (index !== -1) notes.value[index] = note
    if (activeNote.value?.id === id) activeNote.value = note
  }

  async function toggleArchive(id: string, isArchived: boolean) {
    const note = await notesApi.archive(id, isArchived)
    const index = notes.value.findIndex((n) => n.id === id)
    if (index !== -1) notes.value[index] = note
    if (activeNote.value?.id === id) activeNote.value = note
  }

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
