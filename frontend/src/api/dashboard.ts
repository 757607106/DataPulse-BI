/**
 * Dashboard API 接口
 */
import { request } from '@/utils/http';
import type { DashboardOverview } from '@/types/dashboard';

/**
 * 获取 Dashboard 总览数据
 */
export const getDashboardData = (): Promise<DashboardOverview> => {
  return request.get<DashboardOverview>('/api/v1/dashboard/overview');
};

/**
 * 获取 KPI 数据
 */
export const getKPIData = (): Promise<{
  total_sales: number;
  gross_profit: number;
  order_count: number;
  gross_profit_rate: number | null;
}> => {
  return request.get('/api/v1/dashboard/kpi');
};
