/**
 * 用户状态管理 Store
 */
import { defineStore } from 'pinia';
import { ref } from 'vue';
import { ElMessage } from 'element-plus';
import { login as loginApi, getUserInfo, type LoginRequest } from '@/api/auth';

/**
 * 用户信息接口
 */
interface UserState {
  token: string | null;
  username: string;
  role: string;
  isActive: boolean;
}

export const useUserStore = defineStore('user', () => {
  // 状态
  const token = ref<string | null>(localStorage.getItem('access_token'));
  const username = ref<string>('');
  const role = ref<string>('');
  const isActive = ref<boolean>(false);

  /**
   * 用户登录
   */
  const login = async (loginData: LoginRequest): Promise<boolean> => {
    try {
      // 调用登录 API
      const result = await loginApi(loginData);
      
      // 保存 Token 到 LocalStorage
      localStorage.setItem('access_token', result.access_token);
      token.value = result.access_token;

      // 获取用户信息
      await fetchUserInfo();

      ElMessage.success('登录成功');
      return true;
    } catch (error: any) {
      console.error('登录失败:', error);
      ElMessage.error(error.response?.data?.detail || '登录失败，请检查用户名和密码');
      return false;
    }
  };

  /**
   * 获取用户信息
   */
  const fetchUserInfo = async () => {
    try {
      const userInfo = await getUserInfo();
      username.value = userInfo.username;
      role.value = userInfo.role;
      isActive.value = userInfo.is_active;
    } catch (error) {
      console.error('获取用户信息失败:', error);
      // 如果获取用户信息失败，清除登录状态
      logout();
      throw error;
    }
  };

  /**
   * 用户登出
   */
  const logout = () => {
    // 清除 Token
    localStorage.removeItem('access_token');
    token.value = null;
    
    // 重置用户信息
    username.value = '';
    role.value = '';
    isActive.value = false;

    ElMessage.info('已退出登录');
  };

  /**
   * 检查是否已登录
   */
  const isLoggedIn = () => {
    return !!token.value;
  };

  /**
   * 检查是否为管理员
   */
  const isAdmin = () => {
    return role.value === 'admin';
  };

  return {
    // 状态
    token,
    username,
    role,
    isActive,
    
    // 方法
    login,
    logout,
    fetchUserInfo,
    isLoggedIn,
    isAdmin,
  };
});
