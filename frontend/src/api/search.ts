/**
 * @module api/search
 * @description Full-text search API endpoint for finding notes by keyword.
 */

import client from './client'
import type { Note } from '@/types/note'
import type { PaginatedResponse } from '@/types/common'

/** Search API methods. */
export const searchApi = {
  /**
   * Search for notes matching a query string.
   *
   * @param params - Search parameters.
   * @param params.q          - The search query string.
   * @param params.notebook_id - Limit results to a specific notebook (optional).
   * @param params.page        - Page number (1-based).
   * @param params.size        - Items per page.
   * @returns Paginated list of matching notes.
   *
   * @example
   * ```ts
   * const results = await searchApi.search({ q: 'meeting notes', size: 20 })
   * ```
   */
  search(params: { q: string; notebook_id?: string; page?: number; size?: number }): Promise<PaginatedResponse<Note>> {
    return client.get('/search', { params }).then((r) => r.data)
  },
}
