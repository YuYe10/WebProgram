/**
 * @module types/note
 * @description Type definitions for notes — the core content entity that
 * belongs to a notebook and can be tagged, pinned, and archived.
 * 笔记的类型定义——属于笔记本的核心内容实体，可以被标记、置顶和归档。
 */

import type { Tag } from './tag'

/** Represents a note returned by the API.
 * 表示API返回的笔记。
 */
export interface Note {
  /** Unique identifier (UUID).
   * 唯一标识符(UUID)。
   */
  id: string
  /** ID of the parent notebook.
   * 父笔记本的ID。
   */
  notebook_id: string
  /** ID of the owning user.
   * 拥有者用户的ID。
   */
  user_id: string
  /** Note title.
   * 笔记标题。
   */
  title: string
  /** Rich-text content as a JSON object (e.g. TipTap/ProseMirror doc), or `null` if empty.
   * 富文本内容作为JSON对象（例如TipTap/ProseMirror文档），如果为空则为`null`。
   */
  content: Record<string, any> | null
  /** Plain-text representation of the content, used for search indexing.
   * 内容的纯文本表示，用于搜索索引。
   */
  plain_text: string | null
  /** Whether the note is pinned to the top of its notebook.
   * 笔记是否置顶到其笔记本顶部。
   */
  is_pinned: boolean
  /** Whether the note is archived.
   * 笔记是否已归档。
   */
  is_archived: boolean
  /** ISO-8601 timestamp when the note was archived, or `null`.
   * 笔记归档时的ISO-8601时间戳，或`null`。
   */
  archived_at: string | null
  /** Name of the parent notebook (optional, populated by some endpoints).
   * 父笔记本的名称（可选，由某些端点填充）。
   */
  notebook_name?: string
  /** ISO-8601 timestamp when the note was created.
   * 笔记创建时的ISO-8601时间戳。
   */
  created_at: string
  /** ISO-8601 timestamp when the note was last updated.
   * 笔记最后更新时的ISO-8601时间戳。
   */
  updated_at: string
  /** Tags attached to the note (optional, populated by some endpoints).
   * 附加到笔记的标签（可选，由某些端点填充）。
   */
  tags?: Tag[]
}

/** Payload for creating a new note.
 * 创建新笔记的负载。
 */
export interface NoteCreateRequest {
  /** Note title.
   * 笔记标题。
   */
  title: string
  /** Rich-text content as a JSON object (optional at creation).
   * 富文本内容作为JSON对象（创建时可选）。
   */
  content?: Record<string, any>
  /** IDs of tags to attach immediately (optional).
   * 要立即附加的标签ID（可选）。
   */
  tag_ids?: string[]
}

/** Payload for updating an existing note. All fields are optional.
 * 更新现有笔记的负载。所有字段都是可选的。
 */
export interface NoteUpdateRequest {
  /** New title.
   * 新标题。
   */
  title?: string
  /** New rich-text content.
   * 新的富文本内容。
   */
  content?: Record<string, any>
  /** Toggle pinned status.
   * 切换置顶状态。
   */
  is_pinned?: boolean
  /** Toggle archived status.
   * 切换归档状态。
   */
  is_archived?: boolean
}
