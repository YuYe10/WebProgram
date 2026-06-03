<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useNotebooksStore } from '@/stores/notebooks'
import { useUiStore } from '@/stores/ui'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const notebooksStore = useNotebooksStore()
const ui = useUiStore()
const auth = useAuthStore()

onMounted(() => {
  notebooksStore.fetchNotebooks()
})

function goToNotebook(id: string) {
  router.push({ name: 'notebook-detail', params: { id } })
}

function isActive(id: string) {
  return route.params.id === id
}

const NAV_ITEMS = [
  { to: '/notes', icon: 'i-ph-note-pencil', label: 'All Notes' },
  { to: '/archived', icon: 'i-ph-archive-box', label: 'Archived' },
  { to: '/tags', icon: 'i-ph-tag', label: 'Tags' },
]
</script>

<template>
  <aside
    :class="[
      'fixed left-0 top-0 bottom-0 z-30 flex flex-col border-r border-gray-200 dark:border-gray-800 transition-all duration-300',
      'bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl',
      ui.sidebarOpen ? 'w-64 translate-x-0' : 'w-64 -translate-x-full',
    ]"
  >
    <!-- Logo -->
    <div class="flex items-center gap-3 px-5 py-4 border-b border-gray-200 dark:border-gray-800">
      <div class="w-8 h-8 rounded-lg bg-brand-500 flex items-center justify-center flex-shrink-0">
        <span class="i-ph-notepad w-5 h-5 text-white" />
      </div>
      <span class="font-bold text-lg tracking-tight">Noteworthy</span>
    </div>

    <!-- Quick nav -->
    <nav class="flex flex-col gap-1 px-3 py-4">
      <router-link
        v-for="item in NAV_ITEMS"
        :key="item.to"
        :to="item.to"
        :class="[
          'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200',
          route.path === item.to
            ? 'bg-brand-50 dark:bg-brand-900/30 text-brand-600 dark:text-brand-400'
            : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800',
        ]"
      >
        <span :class="item.icon" class="w-5 h-5" />
        {{ item.label }}
      </router-link>
    </nav>

    <div class="mx-4 border-t border-gray-200 dark:border-gray-800" />

    <!-- Notebooks header -->
    <div class="flex items-center justify-between px-5 py-3">
      <span class="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider">
        Notebooks
      </span>
      <button
        class="w-6 h-6 flex items-center justify-center rounded-md text-gray-400 hover:text-brand-500 hover:bg-brand-50 dark:hover:bg-brand-900/30 transition-colors"
        @click="router.push('/')"
      >
        <span class="i-ph-plus w-4 h-4" />
      </button>
    </div>

    <!-- Notebook list -->
    <div class="flex-1 overflow-y-auto px-3 pb-4">
      <div v-if="notebooksStore.isLoading" class="space-y-2 px-2">
        <div v-for="i in 4" :key="i" class="skeleton h-9 rounded-lg" />
      </div>
      <div v-else-if="notebooksStore.notebooks.length === 0" class="px-3 py-8 text-center">
        <p class="text-xs text-gray-400">No notebooks yet</p>
      </div>
      <button
        v-for="nb in notebooksStore.notebooks"
        :key="nb.id"
        :class="[
          'w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-left transition-all duration-200 group',
          isActive(nb.id)
            ? 'bg-brand-50 dark:bg-brand-900/30 text-brand-600 dark:text-brand-400'
            : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800',
        ]"
        @click="goToNotebook(nb.id)"
      >
        <span :class="nb.icon || 'i-ph-notebook'" class="w-5 h-5 flex-shrink-0" :style="{ color: nb.color }" />
        <span class="truncate flex-1">{{ nb.name }}</span>
        <span class="text-xs opacity-50">{{ nb.note_count || 0 }}</span>
      </button>
    </div>

    <!-- User area -->
    <div class="p-3 border-t border-gray-200 dark:border-gray-800">
      <div class="flex items-center gap-3 px-2 py-2 rounded-lg">
        <div class="w-8 h-8 rounded-full bg-brand-100 dark:bg-brand-800 flex items-center justify-center flex-shrink-0">
          <span class="text-brand-600 dark:text-brand-300 font-semibold text-sm">
            {{ auth.user?.display_name?.charAt(0) || auth.user?.username?.charAt(0) || '?' }}
          </span>
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium truncate">{{ auth.user?.display_name || auth.user?.username }}</p>
          <p class="text-xs text-gray-400 truncate">{{ auth.user?.email }}</p>
        </div>
        <button
          class="w-7 h-7 flex items-center justify-center rounded-md text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/30 transition-colors"
          title="Logout"
          @click="auth.logout()"
        >
          <span class="i-ph-sign-out w-4 h-4" />
        </button>
      </div>
    </div>
  </aside>
</template>
