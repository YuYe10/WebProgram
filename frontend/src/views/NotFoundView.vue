<script setup lang="ts">
/**
 * @component NotFoundView
 * @description 404 page displayed when the user navigates to an undefined route.
 * Shows a ghost icon, "404" heading, and a button to navigate back to the dashboard.
 * 
 * 当用户导航到未定义的路由时显示的404页面。
 * 显示幽灵图标、"404"标题和返回仪表板的按钮。
 *
 * @dependencies
 * - UiButton: shared UI button component
 *             共享UI按钮组件
 *
 * @example
 * <!-- Rendered as a catch-all fallback route -->
 * <!-- 作为兜底路由渲染 -->
 * <NotFoundView />
 */
import UiButton from '@/components/ui/UiButton.vue'
</script>

<template>
  <div class="min-h-screen flex items-center justify-center">
    <div class="text-center">
      <div class="w-24 h-24 rounded-3xl bg-gray-100 dark:bg-gray-800 flex items-center justify-center mx-auto mb-6 float">
        <span class="i-ph-ghost w-12 h-12 text-gray-400" />
      </div>
      <h1 class="text-4xl font-bold mb-2">404</h1>
      <p class="text-gray-500 dark:text-gray-400 mb-8">Page not found</p>
      <UiButton variant="primary" @click="$router.push('/')">
        <span class="i-ph-house w-5 h-5" />
        Back to Dashboard
      </UiButton>
    </div>
  </div>
</template>
