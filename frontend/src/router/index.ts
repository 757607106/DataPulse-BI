import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/dashboard'
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
  next()
})

export default router
