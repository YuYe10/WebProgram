/**
 * @module types/tag
 * @description Type definitions for tags — labels that can be attached to
 * notes for categorisation and filtering.
 * 标签的类型定义——可以附加到笔记上进行分类和过滤的标签。
 */

/** Represents a tag returned by the API.
 * 表示API返回的标签。
 */
export interface Tag {
  /** Unique identifier (UUID).
   * 唯一标识符(UUID)。
   */
  id: string
  /** ID of the owning user.
   * 拥有者用户的ID。
   */
  user_id: string
  /** Tag name (unique per user).
   * 标签名称（每个用户唯一）。
   */
  name: string
  /** CSS color value for display.
   * 用于显示的CSS颜色值。
   */
  color: string
  /** ISO-8601 timestamp when the tag was created.
   * 标签创建时的ISO-8601时间戳。
   */
  created_at: string
  /** Number of notes using this tag (optional, populated by some endpoints).
   * 使用此标签的笔记数量（可选，由某些端点填充）。
   */
  note_count?: number
}

/** Payload for creating a new tag.
 * 创建新标签的负载。
 */
export interface TagCreateRequest {
  /** Tag name (required).
   * 标签名称（必填）。
   */
  name: string
  /** CSS color value (optional).
   * CSS颜色值（可选）。
   */
  color?: string
}

/** Payload for updating an existing tag. All fields are optional.
 * 更新现有标签的负载。所有字段都是可选的。
 */
export interface TagUpdateRequest {
  /** New name.
   * 新名称。
   */
  name?: string
  /** New color.
   * 新颜色。
   */
  color?: string
}
