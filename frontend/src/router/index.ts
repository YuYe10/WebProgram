/**
 * @module router/index
 * @description Vue Router configuration. Defines all application routes with
 * lazy-loaded components, layout wrappers, and meta fields for auth/guest
 * access control. The global {@link authGuard} is registered as a
 * `beforeEach` hook.
 * Vue Router配置。定义所有应用路由，包含懒加载组件、布局包装器和用于认证/访客
 * 访问控制的meta字段。全局{@link authGuard}注册为`beforeEach`钩子。
 */

import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { authGuard } from './guards'

/** Application route definitions.
 * 应用路由定义。
 */
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('@/layouts/DefaultLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'dashboard',
        component: () => import('@/views/DashboardView.vue'),
      },
      {
        path: 'notes',
        name: 'all-notes',
        component: () => import('@/views/AllNotesView.vue'),
      },
      {
        path: 'archived',
        name: 'archived',
        component: () => import('@/views/ArchivedView.vue'),
      },
      {
        path: 'tags',
        name: 'tags-manage',
        component: () => import('@/views/TagsManageView.vue'),
      },
      {
        path: 'search',
        name: 'search',
        component: () => import('@/views/SearchView.vue'),
      },
      {
        path: 'notebook/:id',
        name: 'notebook-detail',
        component: () => import('@/views/NotebookDetailView.vue'),
      },
      {
        path: 'notebook/:notebookId/note/:noteId',
        name: 'note-edit',
        component: () => import('@/views/NoteEditView.vue'),
      },
    ],
  },
  {
    path: '/auth',
    component: () => import('@/layouts/AuthLayout.vue'),
    meta: { requiresGuest: true },
    children: [
      {
        path: 'login',
        name: 'login',
        component: () => import('@/views/LoginView.vue'),
      },
      {
        path: 'register',
        name: 'register',
        component: () => import('@/views/RegisterView.vue'),
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFoundView.vue'),
  },
]

/** Vue Router instance with HTML5 history mode.
 * 使用HTML5历史模式的Vue Router实例。
 */
const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Register the global navigation guard for authentication checks
// 注册全局导航守卫用于认证检查
router.beforeEach(authGuard)

export default router
