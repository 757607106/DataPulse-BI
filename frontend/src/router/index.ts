import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { ElMessage } from 'element-plus'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login/index.vue'),
    meta: {
      title: '用户登录',
      requiresAuth: false
    }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard/index.vue'),
    meta: {
      title: '经营驾驶舱',
      icon: 'dashboard'
    }
  },
  {
    path: '/analysis',
    name: 'Analysis',
    component: () => import('@/views/Analysis/index.vue'),
    meta: {
      title: '智能分析',
      icon: 'analysis'
    }
  },
  {
    path: '/reports',
    name: 'Reports',
    component: () => import('@/views/Reports/index.vue'),
    meta: {
      title: '报表中心',
      icon: 'reports'
    }
  },
  {
    path: '/operations',
    name: 'Operations',
    component: () => import('@/views/Operations/index.vue'),
    meta: {
      title: '业务操作',
      icon: 'operations'
    }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/Settings/index.vue'),
    meta: {
      title: '系统设置',
      icon: 'settings'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 进销存智能 BI 系统`
  }

  // 检查是否需要登录
  const token = localStorage.getItem('access_token')
  const requiresAuth = to.meta.requiresAuth !== false // 默认需要认证

  if (requiresAuth && !token) {
    // 需要认证但没有 token，跳转到登录页
    ElMessage.warning('请先登录')
    next({ path: '/login', query: { redirect: to.fullPath } })
  } else if (to.path === '/login' && token) {
    // 已登录用户访问登录页，跳转到首页
    next('/dashboard')
  } else {
    next()
  }
})

export default router
