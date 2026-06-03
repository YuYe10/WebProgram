export interface Notebook {
  id: string
  user_id: string
  name: string
  description: string | null
  icon: string
  color: string
  sort_order: number
  is_archived: boolean
  created_at: string
  updated_at: string
  note_count?: number
}

export interface NotebookCreateRequest {
  name: string
  description?: string
  icon?: string
  color?: string
}

export interface NotebookUpdateRequest {
  name?: string
  description?: string
  icon?: string
  color?: string
  sort_order?: number
  is_archived?: boolean
}
