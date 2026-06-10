import type { Tag } from './tag'

export interface Note {
  id: string
  notebook_id: string
  user_id: string
  title: string
  content: Record<string, any> | null
  plain_text: string | null
  is_pinned: boolean
  is_archived: boolean
  notebook_name?: string
  created_at: string
  updated_at: string
  tags?: Tag[]
}

export interface NoteCreateRequest {
  title: string
  content?: Record<string, any>
  tag_ids?: string[]
}

export interface NoteUpdateRequest {
  title?: string
  content?: Record<string, any>
  is_pinned?: boolean
  is_archived?: boolean
}
