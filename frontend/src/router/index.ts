import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { authGuard } from './guards'

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

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(authGuard)

export default router
