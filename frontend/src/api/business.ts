/**
 * 业务操作相关 API
 */
import { request } from '@/utils/http';

/**
 * 订单明细
 */
export interface OrderItem {
  product_id: number;
  quantity: number;
  price: number;
}

/**
 * AI 指令解析请求
 */
export interface ParseCommandRequest {
  command: string;
}

/**
 * AI 指令解析结果
 */
export interface ParseCommandResult {
  operation_type: 'inbound' | 'outbound';
  items: OrderItem[];
  warehouse_id?: number;
  partner_id?: number;
  salesman_id?: number;
  remark?: string;
  confidence: number;
  explanation: string;
}

/**
 * 入库请求
 */
export interface InboundRequest {
  supplier_id: number;
  warehouse_id: number;
  salesman_id: number;
  items: OrderItem[];
  remark?: string;
}

/**
 * 出库请求
 */
export interface OutboundRequest {
  customer_id: number;
  warehouse_id: number;
  salesman_id: number;
  items: OrderItem[];
  remark?: string;
}

/**
 * 订单响应
 */
export interface OrderResponse {
  id: number;
  order_no: string;
  type: string;
  order_date: string;
  status: string;
  salesman_id: number;
  partner_id: number;
  warehouse_id: number;
  total_amount: number;
  remark?: string;
  created_at: string;
  items: any[];
}

/**
 * 业务操作响应
 */
export interface BusinessOperationResponse {
  success: boolean;
  message: string;
  order?: OrderResponse;
}

/**
 * 商品信息
 */
export interface Product {
  id: number;
  name: string;
  category: string;
  specification?: string;
  unit: string;
  cost_price: number;
  min_stock?: number;
  is_active: boolean;
}

/**
 * 仓库信息
 */
export interface Warehouse {
  id: number;
  name: string;
  address?: string;
  is_active: boolean;
}

/**
 * 合作伙伴信息
 */
export interface Partner {
  id: number;
  name: string;
  type: string;
  region?: string;
  is_active: boolean;
}

/**
 * 业务员信息
 */
export interface Salesman {
  id: number;
  name: string;
  dept_id: number;
  is_active: boolean;
}

/**
 * AI 解析自然语言指令
 */
export const parseCommand = (data: ParseCommandRequest): Promise<ParseCommandResult> => {
  return request.post<ParseCommandResult>('/api/v1/business/parse-command', data);
};

/**
 * 采购入库
 */
export const inbound = (data: InboundRequest): Promise<BusinessOperationResponse> => {
  return request.post<BusinessOperationResponse>('/api/v1/business/inbound', data);
};

/**
 * 销售出库
 */
export const outbound = (data: OutboundRequest): Promise<BusinessOperationResponse> => {
  return request.post<BusinessOperationResponse>('/api/v1/business/outbound', data);
};

/**
 * 获取商品列表（用于下拉选择）
 */
export const getProducts = (): Promise<Product[]> => {
  return request.get<Product[]>('/api/v1/business/products');
};

/**
 * 获取仓库列表
 */
export const getWarehouses = (): Promise<Warehouse[]> => {
  return request.get<Warehouse[]>('/api/v1/business/warehouses');
};

/**
 * 获取合作伙伴列表
 */
export const getPartners = (type?: 'customer' | 'supplier'): Promise<Partner[]> => {
  const url = type ? `/api/v1/business/partners?type=${type}` : '/api/v1/business/partners';
  return request.get<Partner[]>(url);
};

/**
 * 获取业务员列表
 */
export const getSalesmen = (): Promise<Salesman[]> => {
  return request.get<Salesman[]>('/api/v1/business/salesmen');
};
