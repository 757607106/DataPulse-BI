/**
 * 认证相关 API
 */
import { request } from '@/utils/http';

/**
 * 登录请求参数
 */
export interface LoginRequest {
  username: string;
  password: string;
}

/**
 * 登录响应结果
 */
export interface LoginResult {
  access_token: string;
  token_type: string;
}

/**
 * 用户信息
 */
export interface UserInfo {
  id: number;
  username: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

/**
 * 用户登录
 */
export const login = (data: LoginRequest): Promise<LoginResult> => {
  return request.post<LoginResult>('/api/v1/auth/login', data);
};

/**
 * 获取当前用户信息
 */
export const getUserInfo = (): Promise<UserInfo> => {
  return request.get<UserInfo>('/api/v1/auth/me');
};
