/**
 * @module stores/ui
 * @description Pinia store for global UI state: sidebar visibility, theme
 * management (light/dark/system), and toast notifications. Theme changes are
 * persisted to localStorage and applied to the document root element.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

/** Represents a single toast notification displayed to the user. */
export interface Toast {
  /** Unique identifier generated on creation. */
  id: string
  /** Visual variant of the toast. */
  type: 'success' | 'error' | 'info' | 'warning'
  /** Human-readable message. */
  message: string
  /** Auto-dismiss delay in milliseconds (default: 4000). Set to 0 for persistent toasts. */
  duration?: number
}

export const useUiStore = defineStore('ui', () => {
  // ── State ──────────────────────────────────────────────────────────────────

  /** Whether the sidebar is visible. */
  const sidebarOpen = ref(true)

  /** Whether the sidebar is collapsed (icon-only mode). */
  const sidebarCollapsed = ref(false)

  /** Current theme preference. Persisted in localStorage. */
  const theme = ref<'light' | 'dark' | 'system'>(
    (localStorage.getItem('theme') as 'light' | 'dark' | 'system') || 'system'
  )

  /** Active toast notifications. */
  const toasts = ref<Toast[]>([])

  /** Whether a global loading overlay is shown. */
  const globalLoading = ref(false)

  // ── Getters ────────────────────────────────────────────────────────────────

  /**
   * Resolved theme value derived from the user preference.
   * When set to `'system'`, queries `prefers-color-scheme` to determine
   * whether to use `'light'` or `'dark'`.
   */
  const resolvedTheme = computed(() => {
    if (theme.value === 'system') {
      // Check the OS-level color-scheme preference
      if (typeof window !== 'undefined') {
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
      }
      return 'light'
    }
    return theme.value
  })

  // ── Actions ────────────────────────────────────────────────────────────────

  /** Toggle the sidebar between open and closed. */
  function toggleSidebar() {
    sidebarOpen.value = !sidebarOpen.value
  }

  /**
   * Explicitly set the sidebar open state.
   *
   * @param open - `true` to open, `false` to close.
   */
  function setSidebarOpen(open: boolean) {
    sidebarOpen.value = open
  }

  /**
   * Change the theme preference, persist it, and apply it immediately.
   *
   * @param newTheme - The new theme preference.
   */
  function setTheme(newTheme: 'light' | 'dark' | 'system') {
    theme.value = newTheme
    localStorage.setItem('theme', newTheme)
    applyTheme()
  }

  /**
   * Apply the resolved theme class (`'light'` or `'dark'`) to the document
   * root element, removing the previous theme class.
   */
  function applyTheme() {
    const root = document.documentElement
    root.classList.remove('light', 'dark')
    root.classList.add(resolvedTheme.value)
  }

  /**
   * Add a toast notification. An auto-dismiss timer is set based on
   * {@link Toast.duration} (defaults to 4000 ms).
   *
   * @param toast - Toast data without the auto-generated `id` field.
   */
  function addToast(toast: Omit<Toast, 'id'>) {
    const id = `toast-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`
    const newToast: Toast = { ...toast, id, duration: toast.duration || 4000 }
    toasts.value.push(newToast)
    // Auto-remove the toast after its duration elapses
    if (newToast.duration! > 0) {
      setTimeout(() => removeToast(id), newToast.duration)
    }
  }

  /**
   * Remove a toast notification by its ID.
   *
   * @param id - The toast's unique identifier.
   */
  function removeToast(id: string) {
    toasts.value = toasts.value.filter((t) => t.id !== id)
  }

  // Initialize theme on load and listen for OS-level color-scheme changes
  if (typeof window !== 'undefined') {
    applyTheme()
    // Re-apply theme when the OS preference changes while set to 'system'
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
