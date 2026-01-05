/**
 * 全局主题 Store (支持暗色/浅色模式)
 */
import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useThemeStore = defineStore('theme', () => {
  // 读取本地持久化设置，默认为 dark
  const theme = ref<'dark' | 'light'>(localStorage.getItem('app_theme') === 'light' ? 'light' : 'dark');

  const setTheme = (value: 'dark' | 'light') => {
    theme.value = value;
    try {
      localStorage.setItem('app_theme', value);
    } catch (e) {
      // ignore
    }
    // 更新 html 根节点 class 以支持全局 CSS 变量或 Tailwind dark 模式
    const html = document.documentElement;
    if (value === 'dark') {
      html.classList.add('dark');
    } else {
      html.classList.remove('dark');
    }
  };

  const toggleTheme = () => {
    setTheme(theme.value === 'dark' ? 'light' : 'dark');
  };

  // 初始化生效
  setTheme(theme.value);

  return {
    theme,
    setTheme,
    toggleTheme,
  };
});


