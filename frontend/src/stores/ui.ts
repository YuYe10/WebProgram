import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface Toast {
  id: string
  type: 'success' | 'error' | 'info' | 'warning'
  message: string
  duration?: number
}

export const useUiStore = defineStore('ui', () => {
  const sidebarOpen = ref(true)
  const sidebarCollapsed = ref(false)
  const theme = ref<'light' | 'dark' | 'system'>(
    (localStorage.getItem('theme') as 'light' | 'dark' | 'system') || 'system'
  )
  const toasts = ref<Toast[]>([])
  const globalLoading = ref(false)

  const resolvedTheme = computed(() => {
    if (theme.value === 'system') {
      if (typeof window !== 'undefined') {
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
      }
      return 'light'
    }
    return theme.value
  })

  function toggleSidebar() {
    sidebarOpen.value = !sidebarOpen.value
  }

  function setSidebarOpen(open: boolean) {
    sidebarOpen.value = open
  }

  function setTheme(newTheme: 'light' | 'dark' | 'system') {
    theme.value = newTheme
    localStorage.setItem('theme', newTheme)
    applyTheme()
  }

  function applyTheme() {
    const root = document.documentElement
    root.classList.remove('light', 'dark')
    root.classList.add(resolvedTheme.value)
  }

  function addToast(toast: Omit<Toast, 'id'>) {
    const id = `toast-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`
    const newToast: Toast = { ...toast, id, duration: toast.duration || 4000 }
    toasts.value.push(newToast)
    if (newToast.duration! > 0) {
      setTimeout(() => removeToast(id), newToast.duration)
    }
  }

  function removeToast(id: string) {
    toasts.value = toasts.value.filter((t) => t.id !== id)
  }

  // Initialize theme on load
  if (typeof window !== 'undefined') {
    applyTheme()
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
