/**
 * @module types/common
 * @description Shared type definitions used across the application, including
 * the standard paginated response wrapper and sort-order enum.
 */

/**
 * Generic paginated response wrapper returned by all list endpoints.
 *
 * @typeParam T - The type of items in the `items` array.
 */
export interface PaginatedResponse<T> {
  /** Array of items on the current page. */
  items: T[]
  /** Total number of items across all pages. */
  total: number
  /** Current page number (1-based). */
  page: number
  /** Number of items per page. */
  size: number
  /** Total number of pages. */
  pages: number
}

/** Sort direction for ordered queries. */
export type SortOrder = 'asc' | 'desc'
