<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { Grid, ChatDotRound, Document, Setting, User, SwitchButton, Operation } from '@element-plus/icons-vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { useUserStore } from '@/stores/user';
import { useThemeStore } from '@/stores/theme';

const router = useRouter();
const route = useRoute();
const userStore = useUserStore();

// 使用全局主题 Store
const themeStore = useThemeStore();
const theme = computed(() => themeStore.theme);

const menuItems = [
  { id: 'dashboard', path: '/dashboard', label: '经营驾驶舱', icon: Grid },
  { id: 'operations', path: '/operations', label: '业务操作', icon: Operation },
  { id: 'analysis', path: '/analysis', label: '智能分析', icon: ChatDotRound },
  { id: 'reports', path: '/reports', label: '报表中心', icon: Document },
  { id: 'settings', path: '/settings', label: '系统设置', icon: Setting },
];

const currentPath = computed(() => route.path);

const navigateTo = (path: string) => {
  router.push(path);
};

// 退出登录
const handleLogout = async () => {
  try {
    await ElMessageBox.confirm(
      '确认要退出登录吗？',
      '提示',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );
    
    // 调用 Store 的 logout 方法
    userStore.logout();
    
    // 跳转到登录页
    router.push('/login');
  } catch {
    // 用户取消
  }
};

// 获取当前用户名
const username = computed(() => {
  return userStore.username || '用户';
});

// 获取用户角色
const userRole = computed(() => {
  return userStore.role === 'admin' ? '管理员' : '普通用户';
});

// 切换主题
const toggleTheme = () => {
  themeStore.toggleTheme();
};

// 页面加载时检查登录状态
onMounted(async () => {
  // 如果有 token 但没有用户信息，尝试获取
  if (userStore.token && !userStore.username) {
    try {
      await userStore.fetchUserInfo();
    } catch (error) {
      // 静默处理：Token 无效或过期，用户将被路由守卫重定向到登录页
      console.warn('获取用户信息失败，可能是 Token 已过期');
      // 不显示错误消息，因为 http 拦截器已经处理了跳转
    }
  }
});

// 样式计算
const isDark = computed(() => theme.value === 'dark');
const bgClass = computed(() => isDark.value
  ? 'bg-gradient-to-b from-[#1E293B] to-[#0F172A]' 
  : 'bg-white');
const borderClass = computed(() => isDark.value ? 'border-slate-800' : 'border-[#E5E7EB]');
const textClass = computed(() => isDark.value ? 'text-white' : 'text-[#111827]');
</script>

<template>
  <div :class="['flex h-screen', bgClass, textClass]">
    <!-- Sidebar -->
    <aside :class="['w-64 border-r flex flex-col', bgClass, borderClass]">
      <!-- Logo -->
      <div :class="['h-16 flex items-center px-6 border-b flex-shrink-0', borderClass]">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
            <span class="text-sm text-white font-bold">进</span>
          </div>
          <span :class="['text-lg tracking-tight font-medium', textClass]">进销存管理系统</span>
        </div>
      </div>

      <!-- Navigation -->
      <nav class="p-4 space-y-2 flex-1">
        <button
          v-for="item in menuItems"
          :key="item.id"
          @click="navigateTo(item.path)"
          :class="[
            'w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all text-left',
            currentPath === item.path
              ? 'bg-gradient-to-r from-cyan-500/20 to-blue-500/20 text-cyan-500 border border-cyan-500/30'
              : isDark
              ? 'text-slate-400 hover:text-white hover:bg-slate-800/50'
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
          ]"
        >
          <el-icon :size="20"><component :is="item.icon" /></el-icon>
          <span class="font-medium">{{ item.label }}</span>
        </button>
      </nav>

      <!-- Footer -->
      <div :class="['border-t flex-shrink-0', borderClass]">
        <!-- 用户信息 -->
        <div :class="['p-4 flex items-center gap-3 border-b', borderClass]">
          <div class="w-9 h-9 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
            <el-icon :size="18" class="text-white"><User /></el-icon>
          </div>
          <div class="flex-1 min-w-0">
            <p :class="['text-sm font-medium truncate', textClass]">{{ username }}</p>
            <p :class="['text-xs', isDark ? 'text-slate-500' : 'text-slate-400']">{{ userRole }}</p>
          </div>
        </div>
        
        <!-- 退出按钮 -->
        <div class="p-3">
          <button
            @click="handleLogout"
            :class="[
              'w-full flex items-center gap-2 px-3 py-2 rounded-lg transition-all text-left',
              isDark
                ? 'text-slate-400 hover:text-red-400 hover:bg-red-500/10'
                : 'text-slate-600 hover:text-red-600 hover:bg-red-50'
            ]"
          >
            <el-icon :size="18"><SwitchButton /></el-icon>
            <span class="text-sm font-medium">退出登录</span>
          </button>
        </div>
        
        <!-- 主题切换 -->
        <div class="p-3">
          <button
            @click="toggleTheme"
            class="w-full flex items-center gap-2 px-3 py-2 rounded-lg transition-all text-left bg-slate-700 hover:bg-slate-600 text-slate-200"
          >
            <span class="text-sm font-medium">{{ theme === 'dark' ? '切换到浅色' : '切换到深色' }}</span>
          </button>
        </div>
        
        <!-- 版本信息 -->
        <div class="p-4 pt-0">
          <div :class="['text-xs text-center', isDark ? 'text-slate-600' : 'text-slate-400']">
            <p>© 2026 进销存管理系统</p>
            <p class="mt-1">版本 v3.2.1</p>
          </div>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <main :class="['flex-1 overflow-y-auto', bgClass]">
      <slot />
    </main>
  </div>
</template>

<style scoped>
/* 保持与 React 版本一致的样式 */
</style>
