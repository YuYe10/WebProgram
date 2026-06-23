/**
 * @component DefaultLayout
 * @description Main authenticated layout with a collapsible sidebar, a sticky header,
 *   and a content area. Registers a global Ctrl+K shortcut to focus the search bar.
 *   Includes a mobile overlay that closes the sidebar on tap.
 * 
 * 主要的已认证布局，包含可折叠侧边栏、粘性头部和内容区域。
 * 注册全局Ctrl+K快捷键聚焦搜索栏。包含移动端遮罩，点击可关闭侧边栏。
 *
 * @props None
 *        无属性
 *
 * @emits None
 *        无事件
 *
 * @example
 * <!-- Used as a route layout wrapping authenticated pages -->
 * <!-- 用作路由布局包装已认证页面 -->
 * <DefaultLayout />
 */
<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref } from 'vue'
import { useUiStore } from '@/stores/ui'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import AppHeader from '@/components/layout/AppHeader.vue'

const ui = useUiStore()
/** Template ref to AppHeader for calling `focusSearch()`
 * AppHeader的模板引用，用于调用`focusSearch()`
 */
const headerRef = ref<InstanceType<typeof AppHeader> | null>(null)

/**
 * Global keyboard handler — focuses the search bar on Ctrl+K.
 * 全局键盘处理器——Ctrl+K聚焦搜索栏。
 * @param e - The keyboard event
 *            键盘事件
 */
function handleGlobalKeydown(e: KeyboardEvent) {
  if (e.ctrlKey && e.key === 'k') {
    e.preventDefault()
    headerRef.value?.focusSearch()
  }
}

/** Register the global Ctrl+K shortcut on mount
 * 挂载时注册全局Ctrl+K快捷键
 */
onMounted(() => {
  document.addEventListener('keydown', handleGlobalKeydown)
})

/** Clean up the global keyboard listener on unmount
 * 卸载时清理全局键盘监听器
 */
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
