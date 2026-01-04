<script setup lang="ts">
import { computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { Grid, ChatDotRound, Document, Setting } from '@element-plus/icons-vue';

const router = useRouter();
const route = useRoute();

// 主题设置 - 默认浅色
const theme = 'light';

const menuItems = [
  { id: 'dashboard', path: '/dashboard', label: '进销存看板', icon: Grid },
  { id: 'analysis', path: '/analysis', label: '智能分析', icon: ChatDotRound },
  { id: 'reports', path: '/reports', label: '报表中心', icon: Document },
  { id: 'settings', path: '/settings', label: '系统设置', icon: Setting },
];

const currentPath = computed(() => route.path);

const navigateTo = (path: string) => {
  router.push(path);
};

// 样式计算
const bgClass = computed(() => theme === 'dark' 
  ? 'bg-gradient-to-b from-[#1E293B] to-[#0F172A]' 
  : 'bg-white');
const borderClass = computed(() => theme === 'dark' ? 'border-slate-800' : 'border-[#E5E7EB]');
const textClass = computed(() => theme === 'dark' ? 'text-white' : 'text-[#111827]');
</script>

<template>
  <div class="flex h-screen bg-[#F5F7FA]">
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
              : theme === 'dark'
              ? 'text-slate-400 hover:text-white hover:bg-slate-800/50'
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
          ]"
        >
          <el-icon :size="20"><component :is="item.icon" /></el-icon>
          <span class="font-medium">{{ item.label }}</span>
        </button>
      </nav>

      <!-- Footer -->
      <div :class="['p-4 border-t flex-shrink-0', borderClass]">
        <div :class="['text-xs text-center', theme === 'dark' ? 'text-slate-500' : 'text-slate-400']">
          <p>© 2026 进销存管理系统</p>
          <p class="mt-1">版本 v3.2.1</p>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 overflow-y-auto bg-[#F5F7FA]">
      <slot />
    </main>
  </div>
</template>

<style scoped>
/* 保持与 React 版本一致的样式 */
</style>
