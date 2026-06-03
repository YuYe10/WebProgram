import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { notebooksApi } from '@/api/notebooks'
import type { Notebook, NotebookCreateRequest, NotebookUpdateRequest } from '@/types/notebook'

export const useNotebooksStore = defineStore('notebooks', () => {
  const notebooks = ref<Notebook[]>([])
  const activeNotebook = ref<Notebook | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const activeNotebookId = computed(() => activeNotebook.value?.id || null)

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

  async function createNotebook(data: NotebookCreateRequest): Promise<Notebook> {
    const notebook = await notebooksApi.create(data)
    notebooks.value.unshift(notebook)
    return notebook
  }

  async function updateNotebook(id: string, data: NotebookUpdateRequest): Promise<Notebook> {
    const notebook = await notebooksApi.update(id, data)
    const index = notebooks.value.findIndex((n) => n.id === id)
    if (index !== -1) notebooks.value[index] = notebook
    if (activeNotebook.value?.id === id) activeNotebook.value = notebook
    return notebook
  }

  async function deleteNotebook(id: string) {
    await notebooksApi.delete(id)
    notebooks.value = notebooks.value.filter((n) => n.id !== id)
    if (activeNotebook.value?.id === id) activeNotebook.value = null
  }

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
