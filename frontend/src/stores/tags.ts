import { defineStore } from 'pinia'
import { ref } from 'vue'
import { tagsApi } from '@/api/tags'
import type { Tag, TagCreateRequest, TagUpdateRequest } from '@/types/tag'

export const useTagsStore = defineStore('tags', () => {
  const tags = ref<Tag[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  async function fetchTags() {
    isLoading.value = true
    error.value = null
    try {
      const response = await tagsApi.getAll({ size: 200 })
      tags.value = response.items
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to load tags'
    } finally {
      isLoading.value = false
    }
  }

  async function createTag(data: TagCreateRequest): Promise<Tag> {
    const tag = await tagsApi.create(data)
    tags.value.unshift(tag)
    return tag
  }

  async function updateTag(id: string, data: TagUpdateRequest): Promise<Tag> {
    const tag = await tagsApi.update(id, data)
    const index = tags.value.findIndex((t) => t.id === id)
    if (index !== -1) tags.value[index] = tag
    return tag
  }

  async function deleteTag(id: string) {
    await tagsApi.delete(id)
    tags.value = tags.value.filter((t) => t.id !== id)
  }

  return {
    tags,
    isLoading,
    error,
    fetchTags,
    createTag,
    updateTag,
    deleteTag,
  }
})
