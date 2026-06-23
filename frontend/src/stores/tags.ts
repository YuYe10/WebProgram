/**
 * @module stores/tags
 * @description Pinia store for tag management. Handles fetching, creating,
 * updating, and deleting tags used to categorise notes.
 * Pinia标签管理状态。处理用于分类笔记的标签的获取、创建、更新和删除。
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'
import { tagsApi } from '@/api/tags'
import type { Tag, TagCreateRequest, TagUpdateRequest } from '@/types/tag'

export const useTagsStore = defineStore('tags', () => {
  // ── State ──────────────────────────────────────────────────────────────────
  // ── 状态 ──────────────────────────────────────────────────────────────────

  /** List of tags currently loaded.
   * 当前加载的标签列表。
   */
  const tags = ref<Tag[]>([])

  /** Whether a tag-fetching request is in progress.
   * 标签获取请求是否正在进行中。
   */
  const isLoading = ref(false)

  /** Last error message from a tag operation, or `null`.
   * 标签操作的最后错误消息，或`null`。
   */
  const error = ref<string | null>(null)

  // ── Actions ────────────────────────────────────────────────────────────────
  // ── 操作 ────────────────────────────────────────────────────────────────

  /**
   * Fetch all tags (up to 200 by default).
   * 获取所有标签（默认最多200个）。
   * Replaces the local list with the server response.
   * 用服务器响应替换本地列表。
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
   * 创建新标签。
   * The new tag is prepended to the local list.
   * 新标签被添加到本地列表的开头。
   *
   * @param data - Creation payload (name, optional color).
   *               创建负载（名称、可选颜色）。
   * @returns The newly created tag.
   *          新创建的标签。
   */
  async function createTag(data: TagCreateRequest): Promise<Tag> {
    const tag = await tagsApi.create(data)
    tags.value.unshift(tag)
    return tag
  }

  /**
   * Update an existing tag.
   * 更新现有标签。
   * The local list entry is refreshed on success.
   * 成功时刷新本地列表条目。
   *
   * @param id   - The tag's unique identifier.
   *               标签的唯一标识符。
   * @param data - Fields to update (name, color).
   *               要更新的字段（名称、颜色）。
   * @returns The updated tag.
   *          更新后的标签。
   */
  async function updateTag(id: string, data: TagUpdateRequest): Promise<Tag> {
    const tag = await tagsApi.update(id, data)
    const index = tags.value.findIndex((t) => t.id === id)
    if (index !== -1) tags.value[index] = tag
    return tag
  }

  /**
   * Delete a tag permanently.
   * 永久删除标签。
   * Removes it from the local list.
   * 从本地列表中移除它。
   *
   * @param id - The tag's unique identifier.
   *             标签的唯一标识符。
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
