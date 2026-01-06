/**
 * ChatBI API 接口
 */
import { request } from '@/utils/http';
import type { ChatRequest, ChatResponse } from '@/types/chat';

/**
 * 发送聊天消息到 AI
 */
export const sendMessage = (data: ChatRequest): Promise<ChatResponse> => {
  return request.post<ChatResponse>('/api/v1/chat/', data);
};

/**
 * 获取聊天历史记录
 */
export const getChatHistory = (limit: number = 50): Promise<ChatResponse[]> => {
  return request.get<ChatResponse[]>('/api/v1/chat/history', {
    params: { limit }
  });
};
