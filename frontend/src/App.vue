/**
 * @component App
 * @description Root application component. Applies the resolved theme class to the root element,
 *   renders the current route with a page transition, and mounts the global toast container.
 * 
 * 根应用组件。将解析的主题类应用到根元素，
 * 使用页面过渡渲染当前路由，并挂载全局Toast容器。
 *
 * @props None
 *        无属性
 *
 * @emits None
 *        无事件
 *
 * @example
 * <!-- Mounted by main.ts -->
 * <!-- 由main.ts挂载 -->
 * <App />
 */
<script setup lang="ts">
import { useUiStore } from '@/stores/ui'
import UiToastContainer from '@/components/ui/UiToastContainer.vue'

/** Access the resolved theme for the root class binding
 * 访问解析的主题用于根类绑定
 */
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
