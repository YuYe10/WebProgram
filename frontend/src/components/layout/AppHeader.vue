<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUiStore } from '@/stores/ui'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const ui = useUiStore()
const auth = useAuthStore()
const searchQuery = ref('')

function handleSearch() {
  if (searchQuery.value.trim()) {
    router.push({ name: 'search', query: { q: searchQuery.value.trim() } })
    searchQuery.value = ''
  }
}
</script>

<template>
  <header class="sticky top-0 z-20 h-14 flex items-center gap-4 px-4 glass border-b border-gray-200/50 dark:border-gray-800/50">
    <!-- Mobile menu toggle -->
    <button
      class="lg:hidden w-8 h-8 flex items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
      @click="ui.toggleSidebar()"
    >
      <span class="i-ph-list w-5 h-5" />
    </button>

    <!-- Breadcrumb slot -->
    <div class="flex items-center gap-2 flex-1 min-w-0">
      <slot name="breadcrumb">
        <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Dashboard</span>
      </slot>
    </div>

    <!-- Search bar -->
    <div class="hidden sm:flex items-center gap-2 flex-1 max-w-md">
      <form class="relative w-full" @submit.prevent="handleSearch">
        <span class="i-ph-magnifying-glass absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search notes... (Cmd+K)"
          class="w-full pl-10 pr-4 py-1.5 text-sm rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder:text-gray-400 outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all"
        />
      </form>
    </div>

    <!-- Right actions -->
    <div class="flex items-center gap-1">
      <!-- Theme toggle -->
      <button
        class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        :title="ui.resolvedTheme === 'dark' ? 'Switch to light' : 'Switch to dark'"
        @click="ui.setTheme(ui.resolvedTheme === 'dark' ? 'light' : 'dark')"
      >
        <span v-if="ui.resolvedTheme === 'dark'" class="i-ph-sun w-5 h-5" />
        <span v-else class="i-ph-moon w-5 h-5" />
      </button>

      <slot name="actions" />
    </div>
  </header>
</template>
