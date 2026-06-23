/**
 * @module api/tags
 * @description Tag CRUD API endpoints. Tags are labels that can be attached
 * to notes for categorisation and filtering.
 */

import client from './client'
import type { Tag, TagCreateRequest, TagUpdateRequest } from '@/types/tag'
import type { PaginatedResponse } from '@/types/common'

/** Tag API methods. */
export const tagsApi = {
  /**
   * List all tags with optional pagination.
   *
   * @param params - Optional query parameters.
   * @param params.page - Page number (1-based).
   * @param params.size - Items per page.
   * @returns Paginated list of tags.
   */
  getAll(params?: { page?: number; size?: number }): Promise<PaginatedResponse<Tag>> {
    return client.get('/tags', { params }).then((r) => r.data)
  },

  /**
   * Create a new tag.
   *
   * @param data - Creation payload (name, optional color).
   * @returns The newly created tag.
   */
  create(data: TagCreateRequest): Promise<Tag> {
    return client.post('/tags', data).then((r) => r.data)
  },

  /**
   * Update an existing tag.
   *
   * @param id   - The tag's unique identifier.
   * @param data - Fields to update (name, color).
   * @returns The updated tag.
   */
  update(id: string, data: TagUpdateRequest): Promise<Tag> {
    return client.put(`/tags/${id}`, data).then((r) => r.data)
  },

  /**
   * Delete a tag permanently.
   *
   * @param id - The tag's unique identifier.
   * @returns Resolves when deletion is complete.
   */
  delete(id: string): Promise<void> {
    return client.delete(`/tags/${id}`)
  },
}
