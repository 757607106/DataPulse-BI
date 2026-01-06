/**
 * HTTP 请求封装
 */
import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse } from 'axios';
import { ElMessage } from 'element-plus';

// API 基础配置
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// 创建 axios 实例
const http: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
http.interceptors.request.use(
  (config) => {
    // 从 localStorage 获取 token
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
http.interceptors.response.use(
  (response: AxiosResponse) => {
    return response.data;
  },
  (error) => {
    // 处理 401 未授权错误
    if (error.response?.status === 401) {
      // 清除 token
      localStorage.removeItem('access_token');
      
      // 避免循环跳转和重复提示
      if (window.location.pathname !== '/login') {
        // 只在非登录页面显示错误
        ElMessage.error('登录已过期，请重新登录');
        window.location.href = '/login';
      }
      
      return Promise.reject(new Error('未授权'));
    }
    
    // 处理其他错误
    const message = error.response?.data?.detail || error.message || '请求失败';
    console.error('API Error:', message);
    
    return Promise.reject(error);
  }
);

export default http;

// 导出通用请求方法
export const request = {
  get: <T = any>(url: string, config?: AxiosRequestConfig): Promise<T> => {
    return http.get(url, config);
  },
  post: <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> => {
    return http.post(url, data, config);
  },
  put: <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> => {
    return http.put(url, data, config);
  },
  delete: <T = any>(url: string, config?: AxiosRequestConfig): Promise<T> => {
    return http.delete(url, config);
  },
};
