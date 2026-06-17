/**
 * @module stores/notebooks
 * @description Pinia store for notebook management. Handles fetching, creating,
 * updating, and deleting notebooks, as well as tracking the currently active
 * notebook.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { notebooksApi } from '@/api/notebooks'
import type { Notebook, NotebookCreateRequest, NotebookUpdateRequest } from '@/types/notebook'

export const useNotebooksStore = defineStore('notebooks', () => {
  // ── State ──────────────────────────────────────────────────────────────────

  /** List of notebooks currently loaded. */
  const notebooks = ref<Notebook[]>([])

  /** The notebook currently selected in the sidebar, or `null`. */
  const activeNotebook = ref<Notebook | null>(null)

  /** Whether a notebook-fetching request is in progress. */
  const isLoading = ref(false)

  /** Last error message from a notebook operation, or `null`. */
  const error = ref<string | null>(null)

  // ── Getters ────────────────────────────────────────────────────────────────

  /** ID of the active notebook, or `null` when none is selected. */
  const activeNotebookId = computed(() => activeNotebook.value?.id || null)

  // ── Actions ────────────────────────────────────────────────────────────────

  /**
   * Fetch all notebooks (up to 100 by default).
   * Replaces the local list with the server response.
   */
  async function fetchNotebooks() {
    isLoading.value = true
    error.value = null
    try {
      const response = await notebooksApi.getAll({ size: 100 })
      notebooks.value = response.items
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to load notebooks'
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Create a new notebook.
   * The new notebook is prepended to the local list.
   *
   * @param data - Creation payload.
   * @returns The newly created notebook.
   */
  async function createNotebook(data: NotebookCreateRequest): Promise<Notebook> {
    const notebook = await notebooksApi.create(data)
    notebooks.value.unshift(notebook)
    return notebook
  }

  /**
   * Update an existing notebook.
   * Both the list entry and the active notebook are refreshed on success.
   *
   * @param id   - The notebook's unique identifier.
   * @param data - Fields to update.
   * @returns The updated notebook.
   */
  async function updateNotebook(id: string, data: NotebookUpdateRequest): Promise<Notebook> {
    const notebook = await notebooksApi.update(id, data)
    const index = notebooks.value.findIndex((n) => n.id === id)
    if (index !== -1) notebooks.value[index] = notebook
    if (activeNotebook.value?.id === id) activeNotebook.value = notebook
    return notebook
  }

  /**
   * Delete a notebook permanently.
   * Removes it from the local list and clears the active notebook if it was selected.
   *
   * @param id - The notebook's unique identifier.
   */
  async function deleteNotebook(id: string) {
    await notebooksApi.delete(id)
    notebooks.value = notebooks.value.filter((n) => n.id !== id)
    if (activeNotebook.value?.id === id) activeNotebook.value = null
  }

  /**
   * Set the currently active notebook.
   *
   * @param notebook - The notebook to make active, or `null` to clear.
   */
  function setActiveNotebook(notebook: Notebook | null) {
    activeNotebook.value = notebook
  }

  return {
    notebooks,
    activeNotebook,
    activeNotebookId,
    isLoading,
    error,
    fetchNotebooks,
    createNotebook,
    updateNotebook,
    deleteNotebook,
    setActiveNotebook,
  }
})
