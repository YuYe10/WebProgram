/**
 * @module api/search
 * @description Full-text search API endpoint for finding notes by keyword.
 * 全文搜索API端点，用于通过关键词查找笔记。
 */

import client from './client'
import type { Note } from '@/types/note'
import type { PaginatedResponse } from '@/types/common'

/** Search API methods.
 * 搜索API方法。
 */
export const searchApi = {
  /**
   * Search for notes matching a query string.
   * 搜索匹配查询字符串的笔记。
   *
   * @param params - Search parameters.
   *                 搜索参数。
   * @param params.q          - The search query string.
   *                            搜索查询字符串。
   * @param params.notebook_id - Limit results to a specific notebook (optional).
   *                             将结果限制到特定笔记本（可选）。
   * @param params.page        - Page number (1-based).
   *                             页码（从1开始）。
   * @param params.size        - Items per page.
   *                             每页项目数。
   * @returns Paginated list of matching notes.
   *          分页的匹配笔记列表。
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
