/**
 * @module types/notebook
 * @description Type definitions for notebooks — containers that group related
 * notes together. Notebooks support archiving and custom display properties.
 * 笔记本的类型定义——将相关笔记分组在一起的容器。笔记本支持归档和自定义显示属性。
 */

/** Represents a notebook returned by the API.
 * 表示API返回的笔记本。
 */
export interface Notebook {
  /** Unique identifier (UUID).
   * 唯一标识符(UUID)。
   */
  id: string
  /** ID of the owning user.
   * 拥有者用户的ID。
   */
  user_id: string
  /** Notebook name.
   * 笔记本名称。
   */
  name: string
  /** Optional description of the notebook.
   * 笔记本的可选描述。
   */
  description: string | null
  /** Emoji or icon identifier for display.
   * 用于显示的表情符号或图标标识符。
   */
  icon: string
  /** CSS color value for display.
   * 用于显示的CSS颜色值。
   */
  color: string
  /** Sort order index for manual ordering (lower values appear first).
   * 手动排序的排序顺序索引（值越小越靠前）。
   */
  sort_order: number
  /** Whether the notebook is archived.
   * 笔记本是否已归档。
   */
  is_archived: boolean
  /** ISO-8601 timestamp when the notebook was created.
   * 笔记本创建时的ISO-8601时间戳。
   */
  created_at: string
  /** ISO-8601 timestamp when the notebook was last updated.
   * 笔记本最后更新时的ISO-8601时间戳。
   */
  updated_at: string
  /** Number of notes in the notebook (optional, populated by some endpoints).
   * 笔记本中的笔记数量（可选，由某些端点填充）。
   */
  note_count?: number
}

/** Payload for creating a new notebook.
 * 创建新笔记本的负载。
 */
export interface NotebookCreateRequest {
  /** Notebook name (required).
   * 笔记本名称（必填）。
   */
  name: string
  /** Optional description.
   * 可选描述。
   */
  description?: string
  /** Emoji or icon identifier (optional).
   * 表情符号或图标标识符（可选）。
   */
  icon?: string
  /** CSS color value (optional).
   * CSS颜色值（可选）。
   */
  color?: string
}

/** Payload for updating an existing notebook. All fields are optional.
 * 更新现有笔记本的负载。所有字段都是可选的。
 */
export interface NotebookUpdateRequest {
  /** New name.
   * 新名称。
   */
  name?: string
  /** New description.
   * 新描述。
   */
  description?: string
  /** New icon.
   * 新图标。
   */
  icon?: string
  /** New color.
   * 新颜色。
   */
  color?: string
  /** New sort order index.
   * 新的排序顺序索引。
   */
  sort_order?: number
  /** Toggle archived status.
   * 切换归档状态。
   */
  is_archived?: boolean
}
