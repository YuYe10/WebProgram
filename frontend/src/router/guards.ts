/**
 * @module router/guards
 * @description Navigation guards for route-level access control. The primary
 * guard enforces authentication requirements and guest-only restrictions
 * based on route meta fields.
 */

import type { NavigationGuard } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

/**
 * Global navigation guard that enforces authentication rules:
 *
 * - Routes with `meta.requiresAuth` redirect unauthenticated users to the
 *   login page, preserving the original target path in `query.redirect`.
 * - Routes with `meta.requiresGuest` redirect authenticated users to the
 *   dashboard (e.g. login/register pages should not be visited while logged in).
 * - All other routes are allowed through.
 */
export const authGuard: NavigationGuard = (to, _from, next) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    // Unauthenticated user trying to access a protected route — redirect to login
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else if (to.meta.requiresGuest && auth.isAuthenticated) {
    // Authenticated user trying to access a guest-only route — redirect to dashboard
    next({ name: 'dashboard' })
  } else {
    next()
  }
}
