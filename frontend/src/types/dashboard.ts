/**
 * Dashboard API 类型定义
 */

// KPI 数据
export interface KPIData {
  total_sales: number;
  gross_profit: number;
  order_count: number;
  gross_profit_rate: number | null;
}

// 趋势数据点
export interface TrendPoint {
  date: string;
  sales: number;
  profit: number;
}

// 库存预警
export interface InventoryAlert {
  product_name: string;
  current_stock: number;
  min_stock: number | null;
  warehouse_name: string;
  stock_status: string;
}

// 资金状况
export interface FinanceStatus {
  total_receivable: number;
  total_payable: number;
  total_expense: number;
}

// Dashboard 总览数据
export interface DashboardOverview {
  kpi: KPIData;
  trends: TrendPoint[];
  inventory_alerts: InventoryAlert[];
  finance_status: FinanceStatus;
}
