/**
 * @module api/notebooks
 * @description Notebook CRUD API endpoints. Each notebook is a container for
 * notes and supports archiving, pagination, and sorting.
 */

import client from './client'
import type { Notebook, NotebookCreateRequest, NotebookUpdateRequest } from '@/types/notebook'
import type { PaginatedResponse } from '@/types/common'

/** Notebook API methods. */
export const notebooksApi = {
  /**
   * List all notebooks with optional filtering and pagination.
   *
   * @param params - Optional query parameters for filtering and pagination.
   * @param params.archived - Include archived notebooks when `true`.
   * @param params.page   - Page number (1-based).
   * @param params.size   - Items per page.
   * @returns Paginated list of notebooks.
   */
  getAll(params?: { archived?: boolean; page?: number; size?: number }): Promise<PaginatedResponse<Notebook>> {
    return client.get('/notebooks', { params }).then((r) => r.data)
  },

  /**
   * Fetch a single notebook by its ID.
   *
   * @param id - The notebook's unique identifier.
   * @returns The requested notebook.
   */
  getById(id: string): Promise<Notebook> {
    return client.get(`/notebooks/${id}`).then((r) => r.data)
  },

  /**
   * Create a new notebook.
   *
   * @param data - Creation payload (name, optional description, icon, color).
   * @returns The newly created notebook.
   */
  create(data: NotebookCreateRequest): Promise<Notebook> {
    return client.post('/notebooks', data).then((r) => r.data)
  },

  /**
   * Update an existing notebook.
   *
   * @param id   - The notebook's unique identifier.
   * @param data - Fields to update.
   * @returns The updated notebook.
   */
  update(id: string, data: NotebookUpdateRequest): Promise<Notebook> {
    return client.put(`/notebooks/${id}`, data).then((r) => r.data)
  },

  /**
   * Delete a notebook permanently.
   *
   * @param id - The notebook's unique identifier.
   * @returns Resolves when deletion is complete.
   */
  delete(id: string): Promise<void> {
    return client.delete(`/notebooks/${id}`)
  },
}
