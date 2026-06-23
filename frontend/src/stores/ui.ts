/**
 * @module stores/ui
 * @description Pinia store for global UI state: sidebar visibility, theme
 * management (light/dark/system), and toast notifications. Theme changes are
 * persisted to localStorage and applied to the document root element.
 * Pinia全局UI状态管理：侧边栏可见性、主题管理（浅色/深色/系统）和Toast通知。
 * 主题更改会持久化到localStorage并应用到文档根元素。
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

/** Represents a single toast notification displayed to the user.
 * 表示显示给用户的单个Toast通知。
 */
export interface Toast {
  /** Unique identifier generated on creation.
   * 创建时生成的唯一标识符。
   */
  id: string
  /** Visual variant of the toast.
   * Toast的视觉变体。
   */
  type: 'success' | 'error' | 'info' | 'warning'
  /** Human-readable message.
   * 人类可读的消息。
   */
  message: string
  /** Auto-dismiss delay in milliseconds (default: 4000). Set to 0 for persistent toasts.
   * 自动消失延迟（毫秒），默认为4000。设置为0表示持久显示。
   */
  duration?: number
}

export const useUiStore = defineStore('ui', () => {
  // ── State ──────────────────────────────────────────────────────────────────
  // ── 状态 ──────────────────────────────────────────────────────────────────

  /** Whether the sidebar is visible.
   * 侧边栏是否可见。
   */
  const sidebarOpen = ref(true)

  /** Whether the sidebar is collapsed (icon-only mode).
   * 侧边栏是否折叠（仅图标模式）。
   */
  const sidebarCollapsed = ref(false)

  /** Current theme preference. Persisted in localStorage.
   * 当前主题偏好。持久化在localStorage中。
   */
  const theme = ref<'light' | 'dark' | 'system'>(
    (localStorage.getItem('theme') as 'light' | 'dark' | 'system') || 'system'
  )

  /** Active toast notifications.
   * 活动的Toast通知。
   */
  const toasts = ref<Toast[]>([])

  /** Whether a global loading overlay is shown.
   * 是否显示全局加载遮罩。
   */
  const globalLoading = ref(false)

  // ── Getters ────────────────────────────────────────────────────────────────
  // ── 计算属性 ────────────────────────────────────────────────────────────────

  /**
   * Resolved theme value derived from the user preference.
   * 从用户偏好派生的解析主题值。
   * When set to `'system'`, queries `prefers-color-scheme` to determine
   * whether to use `'light'` or `'dark'`.
   * 设置为`'system'`时，查询`prefers-color-scheme`来决定使用`'light'`还是`'dark'`。
   */
  const resolvedTheme = computed(() => {
    if (theme.value === 'system') {
      // Check the OS-level color-scheme preference
      // 检查操作系统级别的颜色方案偏好
      if (typeof window !== 'undefined') {
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
      }
      return 'light'
    }
    return theme.value
  })

  // ── Actions ────────────────────────────────────────────────────────────────
  // ── 操作 ────────────────────────────────────────────────────────────────

  /** Toggle the sidebar between open and closed.
   * 切换侧边栏的打开和关闭状态。
   */
  function toggleSidebar() {
    sidebarOpen.value = !sidebarOpen.value
  }

  /**
   * Explicitly set the sidebar open state.
   * 显式设置侧边栏的打开状态。
   *
   * @param open - `true` to open, `false` to close.
   *               `true`表示打开，`false`表示关闭。
   */
  function setSidebarOpen(open: boolean) {
    sidebarOpen.value = open
  }

  /**
   * Change the theme preference, persist it, and apply it immediately.
   * 更改主题偏好，持久化并立即应用。
   *
   * @param newTheme - The new theme preference.
   *                   新的主题偏好。
   */
  function setTheme(newTheme: 'light' | 'dark' | 'system') {
    theme.value = newTheme
    localStorage.setItem('theme', newTheme)
    applyTheme()
  }

  /**
   * Apply the resolved theme class (`'light'` or `'dark'`) to the document
   * root element, removing the previous theme class.
   * 将解析的主题类（`'light'`或`'dark'`）应用到文档根元素，移除之前的主题类。
   */
  function applyTheme() {
    const root = document.documentElement
    root.classList.remove('light', 'dark')
    root.classList.add(resolvedTheme.value)
  }

  /**
   * Add a toast notification. An auto-dismiss timer is set based on
   * {@link Toast.duration} (defaults to 4000 ms).
   * 添加Toast通知。基于{@link Toast.duration}设置自动消失计时器（默认为4000毫秒）。
   *
   * @param toast - Toast data without the auto-generated `id` field.
   *                不含自动生成的`id`字段的Toast数据。
   */
  function addToast(toast: Omit<Toast, 'id'>) {
    const id = `toast-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`
    const newToast: Toast = { ...toast, id, duration: toast.duration || 4000 }
    toasts.value.push(newToast)
    // Auto-remove the toast after its duration elapses
    // 在持续时间过后自动移除Toast
    if (newToast.duration! > 0) {
      setTimeout(() => removeToast(id), newToast.duration)
    }
  }

  /**
   * Remove a toast notification by its ID.
   * 根据ID移除Toast通知。
   *
   * @param id - The toast's unique identifier.
   *             Toast的唯一标识符。
   */
  function removeToast(id: string) {
    toasts.value = toasts.value.filter((t) => t.id !== id)
  }

  // Initialize theme on load and listen for OS-level color-scheme changes
  // 加载时初始化主题并监听操作系统级别的颜色方案更改
  if (typeof window !== 'undefined') {
    applyTheme()
    // Re-apply theme when the OS preference changes while set to 'system'
    // 当设置为'system'时，如果操作系统偏好更改则重新应用主题
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
      if (theme.value === 'system') applyTheme()
    })
  }

  return {
    sidebarOpen,
    sidebarCollapsed,
    theme,
    resolvedTheme,
    toasts,
    globalLoading,
    toggleSidebar,
    setSidebarOpen,
    setTheme,
    addToast,
    removeToast,
  }
})
