/**
 * @module types/tag
 * @description Type definitions for tags — labels that can be attached to
 * notes for categorisation and filtering.
 */

/** Represents a tag returned by the API. */
export interface Tag {
  /** Unique identifier (UUID). */
  id: string
  /** ID of the owning user. */
  user_id: string
  /** Tag name (unique per user). */
  name: string
  /** CSS color value for display. */
  color: string
  /** ISO-8601 timestamp when the tag was created. */
  created_at: string
  /** Number of notes using this tag (optional, populated by some endpoints). */
  note_count?: number
}

/** Payload for creating a new tag. */
export interface TagCreateRequest {
  /** Tag name (required). */
  name: string
  /** CSS color value (optional). */
  color?: string
}

/** Payload for updating an existing tag. All fields are optional. */
export interface TagUpdateRequest {
  /** New name. */
  name?: string
  /** New color. */
  color?: string
}
