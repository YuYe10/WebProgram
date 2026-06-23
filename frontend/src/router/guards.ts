/**
 * @module router/guards
 * @description Navigation guards for route-level access control. The primary
 * guard enforces authentication requirements and guest-only restrictions
 * based on route meta fields.
 * 路由级访问控制的导航守卫。主要守卫根据路由meta字段强制执行认证要求和仅访客限制。
 */

import type { NavigationGuard } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

/**
 * Global navigation guard that enforces authentication rules:
 * 全局导航守卫，强制执行认证规则：
 *
 * - Routes with `meta.requiresAuth` redirect unauthenticated users to the
 *   login page, preserving the original target path in `query.redirect`.
 *   带有`meta.requiresAuth`的路由将未认证用户重定向到登录页面，
 *   并在`query.redirect`中保留原始目标路径。
 * - Routes with `meta.requiresGuest` redirect authenticated users to the
 *   dashboard (e.g. login/register pages should not be visited while logged in).
 *   带有`meta.requiresGuest`的路由将已认证用户重定向到仪表板
 *   （例如登录/注册页面不应该在登录状态下访问）。
 * - All other routes are allowed through.
 *   所有其他路由都允许通过。
 */
export const authGuard: NavigationGuard = (to, _from, next) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    // Unauthenticated user trying to access a protected route — redirect to login
    // 未认证用户尝试访问受保护路由——重定向到登录
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else if (to.meta.requiresGuest && auth.isAuthenticated) {
    // Authenticated user trying to access a guest-only route — redirect to dashboard
    // 已认证用户尝试访问仅访客路由——重定向到仪表板
    next({ name: 'dashboard' })
  } else {
    next()
  }
}
