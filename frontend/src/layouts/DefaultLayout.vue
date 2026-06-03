<script setup lang="ts">
import { useUiStore } from '@/stores/ui'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import AppHeader from '@/components/layout/AppHeader.vue'

const ui = useUiStore()
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
      <AppHeader />
      <main class="flex-1 p-4 md:p-6 lg:p-8 overflow-y-auto">
        <router-view />
      </main>
    </div>
  </div>
</template>
