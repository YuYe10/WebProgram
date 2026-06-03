export interface Tag {
  id: string
  user_id: string
  name: string
  color: string
  created_at: string
  note_count?: number
}

export interface TagCreateRequest {
  name: string
  color?: string
}

export interface TagUpdateRequest {
  name?: string
  color?: string
}
