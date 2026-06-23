/**
 * @component App
 * @description Root application component. Applies the resolved theme class to the root element,
 *   renders the current route with a page transition, and mounts the global toast container.
 *
 * @props None
 *
 * @emits None
 *
 * @example
 * <!-- Mounted by main.ts -->
 * <App />
 */
<script setup lang="ts">
import { useUiStore } from '@/stores/ui'
import UiToastContainer from '@/components/ui/UiToastContainer.vue'

/** Access the resolved theme for the root class binding */
const ui = useUiStore()
</script>

<template>
  <!-- Root element applies the resolved theme class ('dark' or 'light') for dark mode support -->
  <div :class="ui.resolvedTheme" class="min-h-screen bg-gray-50 dark:bg-gray-950 text-gray-900 dark:text-gray-100">
    <!-- Route view with page transition animation (fade + slide) -->
    <router-view v-slot="{ Component, route }">
      <transition name="page" mode="out-in">
        <component :is="Component" :key="route.path" />
      </transition>
    </router-view>

    <!-- Global toast notification container -->
    <UiToastContainer />
  </div>
</template>

<style scoped>
.page-enter-active,
.page-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.page-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.page-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
