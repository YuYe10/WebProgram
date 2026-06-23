/**
 * @module stores/notebooks
 * @description Pinia store for notebook management. Handles fetching, creating,
 * updating, and deleting notebooks, as well as tracking the currently active
 * notebook.
 * Pinia笔记本管理状态。处理笔记本的获取、创建、更新和删除，以及跟踪当前活动的笔记本。
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { notebooksApi } from '@/api/notebooks'
import type { Notebook, NotebookCreateRequest, NotebookUpdateRequest } from '@/types/notebook'

export const useNotebooksStore = defineStore('notebooks', () => {
  // ── State ──────────────────────────────────────────────────────────────────
  // ── 状态 ──────────────────────────────────────────────────────────────────

  /** List of notebooks currently loaded.
   * 当前加载的笔记本列表。
   */
  const notebooks = ref<Notebook[]>([])

  /** The notebook currently selected in the sidebar, or `null`.
   * 当前在侧边栏中选中的笔记本，或`null`。
   */
  const activeNotebook = ref<Notebook | null>(null)

  /** Whether a notebook-fetching request is in progress.
   * 笔记本获取请求是否正在进行中。
   */
  const isLoading = ref(false)

  /** Last error message from a notebook operation, or `null`.
   * 笔记本操作的最后错误消息，或`null`。
   */
  const error = ref<string | null>(null)

  // ── Getters ────────────────────────────────────────────────────────────────
  // ── 计算属性 ────────────────────────────────────────────────────────────────

  /** ID of the active notebook, or `null` when none is selected.
   * 活动笔记本的ID，未选中时为`null`。
   */
  const activeNotebookId = computed(() => activeNotebook.value?.id || null)

  // ── Actions ────────────────────────────────────────────────────────────────
  // ── 操作 ────────────────────────────────────────────────────────────────

  /**
   * Fetch all notebooks (up to 100 by default).
   * 获取所有笔记本（默认最多100个）。
   * Replaces the local list with the server response.
   * 用服务器响应替换本地列表。
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
   * 创建新笔记本。
   * The new notebook is prepended to the local list.
   * 新笔记本被添加到本地列表的开头。
   *
   * @param data - Creation payload.
   *               创建负载。
   * @returns The newly created notebook.
   *          新创建的笔记本。
   */
  async function createNotebook(data: NotebookCreateRequest): Promise<Notebook> {
    const notebook = await notebooksApi.create(data)
    notebooks.value.unshift(notebook)
    return notebook
  }

  /**
   * Update an existing notebook.
   * 更新现有笔记本。
   * Both the list entry and the active notebook are refreshed on success.
   * 成功时刷新列表条目和活动笔记本。
   *
   * @param id   - The notebook's unique identifier.
   *               笔记本的唯一标识符。
   * @param data - Fields to update.
   *               要更新的字段。
   * @returns The updated notebook.
   *          更新后的笔记本。
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
   * 永久删除笔记本。
   * Removes it from the local list and clears the active notebook if it was selected.
   * 从本地列表中移除它，如果它被选中则清除活动笔记本。
   *
   * @param id - The notebook's unique identifier.
   *             笔记本的唯一标识符。
   */
  async function deleteNotebook(id: string) {
    await notebooksApi.delete(id)
    notebooks.value = notebooks.value.filter((n) => n.id !== id)
    if (activeNotebook.value?.id === id) activeNotebook.value = null
  }

  /**
   * Set the currently active notebook.
   * 设置当前活动的笔记本。
   *
   * @param notebook - The notebook to make active, or `null` to clear.
   *                   要设为活动的笔记本，或`null`来清除。
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
