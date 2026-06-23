/**
 * @module types/common
 * @description Shared type definitions used across the application, including
 * the standard paginated response wrapper and sort-order enum.
 * 应用程序中共享的类型定义，包括标准分页响应包装器和排序顺序枚举。
 */

/**
 * Generic paginated response wrapper returned by all list endpoints.
 * 所有列表端点返回的通用分页响应包装器。
 *
 * @typeParam T - The type of items in the `items` array.
 * @typeParam T - `items`数组中项目的类型。
 */
export interface PaginatedResponse<T> {
  /** Array of items on the current page.
   * 当前页面的项目数组。
   */
  items: T[]
  /** Total number of items across all pages.
   * 所有页面的项目总数。
   */
  total: number
  /** Current page number (1-based).
   * 当前页码（从1开始）。
   */
  page: number
  /** Number of items per page.
   * 每页项目数。
   */
  size: number
  /** Total number of pages.
   * 总页数。
   */
  pages: number
}

/** Sort direction for ordered queries.
 * 有序查询的排序方向。
 */
export type SortOrder = 'asc' | 'desc'
