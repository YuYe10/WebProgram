/**
 * @module api/tags
 * @description Tag CRUD API endpoints. Tags are labels that can be attached
 * to notes for categorisation and filtering.
 * 标签CRUD API端点。标签是可以附加到笔记上进行分类和过滤的标签。
 */

import client from './client'
import type { Tag, TagCreateRequest, TagUpdateRequest } from '@/types/tag'
import type { PaginatedResponse } from '@/types/common'

/** Tag API methods.
 * 标签API方法。
 */
export const tagsApi = {
  /**
   * List all tags with optional pagination.
   * 列出所有标签，支持可选分页。
   *
   * @param params - Optional query parameters.
   *                 可选查询参数。
   * @param params.page - Page number (1-based).
   *                      页码（从1开始）。
   * @param params.size - Items per page.
   *                      每页项目数。
   * @returns Paginated list of tags.
   *          分页的标签列表。
   */
  getAll(params?: { page?: number; size?: number }): Promise<PaginatedResponse<Tag>> {
    return client.get('/tags', { params }).then((r) => r.data)
  },

  /**
   * Create a new tag.
   * 创建新标签。
   *
   * @param data - Creation payload (name, optional color).
   *               创建负载（名称、可选颜色）。
   * @returns The newly created tag.
   *          新创建的标签。
   */
  create(data: TagCreateRequest): Promise<Tag> {
    return client.post('/tags', data).then((r) => r.data)
  },

  /**
   * Update an existing tag.
   * 更新现有标签。
   *
   * @param id   - The tag's unique identifier.
   *               标签的唯一标识符。
   * @param data - Fields to update (name, color).
   *               要更新的字段（名称、颜色）。
   * @returns The updated tag.
   *          更新后的标签。
   */
  update(id: string, data: TagUpdateRequest): Promise<Tag> {
    return client.put(`/tags/${id}`, data).then((r) => r.data)
  },

  /**
   * Delete a tag permanently.
   * 永久删除标签。
   *
   * @param id - The tag's unique identifier.
   *             标签的唯一标识符。
   * @returns Resolves when deletion is complete.
   *          删除完成时解析。
   */
  delete(id: string): Promise<void> {
    return client.delete(`/tags/${id}`)
  },
}
