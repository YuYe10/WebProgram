/**
 * @module api/notebooks
 * @description Notebook CRUD API endpoints. Each notebook is a container for
 * notes and supports archiving, pagination, and sorting.
 * 笔记本CRUD API端点。每个笔记本是笔记的容器，支持归档、分页和排序。
 */

import client from './client'
import type { Notebook, NotebookCreateRequest, NotebookUpdateRequest } from '@/types/notebook'
import type { PaginatedResponse } from '@/types/common'

/** Notebook API methods.
 * 笔记本API方法。
 */
export const notebooksApi = {
  /**
   * List all notebooks with optional filtering and pagination.
   * 列出所有笔记本，支持可选的过滤和分页。
   *
   * @param params - Optional query parameters for filtering and pagination.
   *                 可选的查询参数，用于过滤和分页。
   * @param params.archived - Include archived notebooks when `true`.
   *                          为`true`时包含已归档的笔记本。
   * @param params.page   - Page number (1-based).
   *                        页码（从1开始）。
   * @param params.size   - Items per page.
   *                        每页项目数。
   * @returns Paginated list of notebooks.
   *          分页的笔记本列表。
   */
  getAll(params?: { archived?: boolean; page?: number; size?: number }): Promise<PaginatedResponse<Notebook>> {
    return client.get('/notebooks', { params }).then((r) => r.data)
  },

  /**
   * Fetch a single notebook by its ID.
   * 根据ID获取单个笔记本。
   *
   * @param id - The notebook's unique identifier.
   *             笔记本的唯一标识符。
   * @returns The requested notebook.
   *          请求的笔记本。
   */
  getById(id: string): Promise<Notebook> {
    return client.get(`/notebooks/${id}`).then((r) => r.data)
  },

  /**
   * Create a new notebook.
   * 创建新笔记本。
   *
   * @param data - Creation payload (name, optional description, icon, color).
   *               创建负载（名称、可选描述、图标、颜色）。
   * @returns The newly created notebook.
   *          新创建的笔记本。
   */
  create(data: NotebookCreateRequest): Promise<Notebook> {
    return client.post('/notebooks', data).then((r) => r.data)
  },

  /**
   * Update an existing notebook.
   * 更新现有笔记本。
   *
   * @param id   - The notebook's unique identifier.
   *               笔记本的唯一标识符。
   * @param data - Fields to update.
   *               要更新的字段。
   * @returns The updated notebook.
   *          更新后的笔记本。
   */
  update(id: string, data: NotebookUpdateRequest): Promise<Notebook> {
    return client.put(`/notebooks/${id}`, data).then((r) => r.data)
  },

  /**
   * Delete a notebook permanently.
   * 永久删除笔记本。
   *
   * @param id - The notebook's unique identifier.
   *             笔记本的唯一标识符。
   * @returns Resolves when deletion is complete.
   *          删除完成时解析。
   */
  delete(id: string): Promise<void> {
    return client.delete(`/notebooks/${id}`)
  },
}
