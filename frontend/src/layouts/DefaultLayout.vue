/**
 * @component DefaultLayout
 * @description Main authenticated layout with a collapsible sidebar, a sticky header,
 *   and a content area. Registers a global Ctrl+K shortcut to focus the search bar.
 *   Includes a mobile overlay that closes the sidebar on tap.
 *
 * @props None
 *
 * @emits None
 *
 * @example
 * <!-- Used as a route layout wrapping authenticated pages -->
 * <DefaultLayout />
 */
<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref } from 'vue'
import { useUiStore } from '@/stores/ui'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import AppHeader from '@/components/layout/AppHeader.vue'

const ui = useUiStore()
/** Template ref to AppHeader for calling `focusSearch()` */
const headerRef = ref<InstanceType<typeof AppHeader> | null>(null)

/**
 * Global keyboard handler — focuses the search bar on Ctrl+K.
 * @param e - The keyboard event
 */
function handleGlobalKeydown(e: KeyboardEvent) {
  if (e.ctrlKey && e.key === 'k') {
    e.preventDefault()
    headerRef.value?.focusSearch()
  }
}

/** Register the global Ctrl+K shortcut on mount */
onMounted(() => {
  document.addEventListener('keydown', handleGlobalKeydown)
})

/** Clean up the global keyboard listener on unmount */
onBeforeUnmount(() => {
  document.removeEventListener('keydown', handleGlobalKeydown)
})
</script>

<template>
  <div class="flex min-h-screen">
    <!-- Sidebar overlay for mobile -->
    <transition name="fade">
      <div
        v-if="ui.sidebarOpen"
        class="fixed inset-0 z-20 bg-black/30 backdrop-blur-sm lg:hidden"
        @click="ui.setSidebarOpen(false)"
      />
    </transition>

    <!-- Sidebar -->
    <AppSidebar />

    <!-- Main area -->
    <div
      :class="[
        'flex-1 flex flex-col min-h-screen transition-all duration-300',
        'lg:ml-64',
      ]"
    >
      <AppHeader ref="headerRef" />
      <main class="flex-1 p-4 md:p-6 lg:p-8 overflow-y-auto">
        <router-view />
      </main>
    </div>
  </div>
</template>
