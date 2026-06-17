/**
 * @module stores/tags
 * @description Pinia store for tag management. Handles fetching, creating,
 * updating, and deleting tags used to categorise notes.
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'
import { tagsApi } from '@/api/tags'
import type { Tag, TagCreateRequest, TagUpdateRequest } from '@/types/tag'

export const useTagsStore = defineStore('tags', () => {
  // ── State ──────────────────────────────────────────────────────────────────

  /** List of tags currently loaded. */
  const tags = ref<Tag[]>([])

  /** Whether a tag-fetching request is in progress. */
  const isLoading = ref(false)

  /** Last error message from a tag operation, or `null`. */
  const error = ref<string | null>(null)

  // ── Actions ────────────────────────────────────────────────────────────────

  /**
   * Fetch all tags (up to 200 by default).
   * Replaces the local list with the server response.
   */
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

  /**
   * Create a new tag.
   * The new tag is prepended to the local list.
   *
   * @param data - Creation payload (name, optional color).
   * @returns The newly created tag.
   */
  async function createTag(data: TagCreateRequest): Promise<Tag> {
    const tag = await tagsApi.create(data)
    tags.value.unshift(tag)
    return tag
  }

  /**
   * Update an existing tag.
   * The local list entry is refreshed on success.
   *
   * @param id   - The tag's unique identifier.
   * @param data - Fields to update (name, color).
   * @returns The updated tag.
   */
  async function updateTag(id: string, data: TagUpdateRequest): Promise<Tag> {
    const tag = await tagsApi.update(id, data)
    const index = tags.value.findIndex((t) => t.id === id)
    if (index !== -1) tags.value[index] = tag
    return tag
  }

  /**
   * Delete a tag permanently.
   * Removes it from the local list.
   *
   * @param id - The tag's unique identifier.
   */
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
