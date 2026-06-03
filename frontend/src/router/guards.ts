import type { NavigationGuard } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

export const authGuard: NavigationGuard = (to, _from, next) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else if (to.meta.requiresGuest && auth.isAuthenticated) {
    next({ name: 'dashboard' })
  } else {
    next()
  }
}
