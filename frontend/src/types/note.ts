/**
 * @module types/note
 * @description Type definitions for notes — the core content entity that
 * belongs to a notebook and can be tagged, pinned, and archived.
 */

import type { Tag } from './tag'

/** Represents a note returned by the API. */
export interface Note {
  /** Unique identifier (UUID). */
  id: string
  /** ID of the parent notebook. */
  notebook_id: string
  /** ID of the owning user. */
  user_id: string
  /** Note title. */
  title: string
  /** Rich-text content as a JSON object (e.g. TipTap/ProseMirror doc), or `null` if empty. */
  content: Record<string, any> | null
  /** Plain-text representation of the content, used for search indexing. */
  plain_text: string | null
  /** Whether the note is pinned to the top of its notebook. */
  is_pinned: boolean
  /** Whether the note is archived. */
  is_archived: boolean
  /** ISO-8601 timestamp when the note was archived, or `null`. */
  archived_at: string | null
  /** Name of the parent notebook (optional, populated by some endpoints). */
  notebook_name?: string
  /** ISO-8601 timestamp when the note was created. */
  created_at: string
  /** ISO-8601 timestamp when the note was last updated. */
  updated_at: string
  /** Tags attached to the note (optional, populated by some endpoints). */
  tags?: Tag[]
}

/** Payload for creating a new note. */
export interface NoteCreateRequest {
  /** Note title. */
  title: string
  /** Rich-text content as a JSON object (optional at creation). */
  content?: Record<string, any>
  /** IDs of tags to attach immediately (optional). */
  tag_ids?: string[]
}

/** Payload for updating an existing note. All fields are optional. */
export interface NoteUpdateRequest {
  /** New title. */
  title?: string
  /** New rich-text content. */
  content?: Record<string, any>
  /** Toggle pinned status. */
  is_pinned?: boolean
  /** Toggle archived status. */
  is_archived?: boolean
}
