/**
 * ChatBI 相关类型定义
 */

// 图表类型枚举
export type ChartType = 'bar' | 'line' | 'pie' | 'table' | 'scatter' | 'radar';

// AI 返回的数据结构
export interface ChatData {
  columns: string[];  // 列名数组
  rows: Array<Record<string, any>>;  // 行数据数组
}

// 后端 ChatBI 接口响应
export interface ChatResponse {
  answer_text: string;  // AI 自然语言回答
  sql: string;          // 生成的 SQL 语句
  data: ChatData;       // 查询结果数据
  chart_type: ChartType; // 推荐的图表类型
}

// 聊天消息接口
export interface ChatMessage {
  id: number;
  type: 'user' | 'ai';
  content: string;  // 用户消息或 AI 文本回答
  timestamp: Date;
  
  // AI 消息的额外字段
  sql?: string;
  data?: ChatData;
  chartType?: ChartType;
  
  // 加载状态
  loading?: boolean;
  loadingStage?: 'thinking' | 'generating' | 'querying' | 'done';
}

// 加载阶段描述
export const LOADING_STAGES = {
  thinking: 'AI 正在思考...',
  generating: '生成 SQL 查询...',
  querying: '执行查询中...',
  done: '完成'
} as const;

// API 请求参数
export interface ChatRequest {
  question: string;
  context?: Record<string, any>;
}
