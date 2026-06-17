/**
 * @module types/notebook
 * @description Type definitions for notebooks — containers that group related
 * notes together. Notebooks support archiving and custom display properties.
 */

/** Represents a notebook returned by the API. */
export interface Notebook {
  /** Unique identifier (UUID). */
  id: string
  /** ID of the owning user. */
  user_id: string
  /** Notebook name. */
  name: string
  /** Optional description of the notebook. */
  description: string | null
  /** Emoji or icon identifier for display. */
  icon: string
  /** CSS color value for display. */
  color: string
  /** Sort order index for manual ordering (lower values appear first). */
  sort_order: number
  /** Whether the notebook is archived. */
  is_archived: boolean
  /** ISO-8601 timestamp when the notebook was created. */
  created_at: string
  /** ISO-8601 timestamp when the notebook was last updated. */
  updated_at: string
  /** Number of notes in the notebook (optional, populated by some endpoints). */
  note_count?: number
}

/** Payload for creating a new notebook. */
export interface NotebookCreateRequest {
  /** Notebook name (required). */
  name: string
  /** Optional description. */
  description?: string
  /** Emoji or icon identifier (optional). */
  icon?: string
  /** CSS color value (optional). */
  color?: string
}

/** Payload for updating an existing notebook. All fields are optional. */
export interface NotebookUpdateRequest {
  /** New name. */
  name?: string
  /** New description. */
  description?: string
  /** New icon. */
  icon?: string
  /** New color. */
  color?: string
  /** New sort order index. */
  sort_order?: number
  /** Toggle archived status. */
  is_archived?: boolean
}
