"""
业务操作相关的 Pydantic 模型
"""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field


# ==================== 商品相关 ====================

class ProductCreate(BaseModel):
    """创建商品请求"""
    name: str = Field(..., description="商品名称")
    category: str = Field(..., description="商品分类")
    specification: Optional[str] = Field(None, description="规格型号")
    unit: str = Field(default="件", description="计量单位")
    cost_price: Decimal = Field(..., gt=0, description="成本价")
    min_stock: Optional[Decimal] = Field(None, description="最低库存预警线")


class ProductResponse(BaseModel):
    """商品响应"""
    id: int
    name: str
    category: str
    specification: Optional[str]
    unit: str
    cost_price: Decimal
    min_stock: Optional[Decimal]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== 入库/出库相关 ====================

class OrderItemCreate(BaseModel):
    """订单明细"""
    product_id: int = Field(..., description="商品ID")
    quantity: Decimal = Field(..., gt=0, description="数量")
    price: Decimal = Field(..., gt=0, description="单价")


class InboundRequest(BaseModel):
    """采购入库请求"""
    supplier_id: int = Field(..., description="供应商ID")
    warehouse_id: int = Field(..., description="仓库ID")
    salesman_id: int = Field(..., description="业务员ID")
    items: List[OrderItemCreate] = Field(..., min_items=1, description="商品明细列表")
    remark: Optional[str] = Field(None, description="备注")


class OutboundRequest(BaseModel):
    """销售出库请求"""
    customer_id: int = Field(..., description="客户ID")
    warehouse_id: int = Field(..., description="仓库ID")
    salesman_id: int = Field(..., description="业务员ID")
    items: List[OrderItemCreate] = Field(..., min_items=1, description="商品明细列表")
    remark: Optional[str] = Field(None, description="备注")


class OrderItemResponse(BaseModel):
    """订单明细响应"""
    id: int
    product_id: int
    quantity: Decimal
    price: Decimal
    subtotal: Decimal
    remark: Optional[str]
    
    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    """订单响应"""
    id: int
    order_no: str
    type: str
    order_date: datetime
    status: str
    salesman_id: int
    partner_id: int
    warehouse_id: int
    total_amount: Decimal
    remark: Optional[str]
    created_at: datetime
    items: List[OrderItemResponse] = []
    
    class Config:
        from_attributes = True


class BusinessOperationResponse(BaseModel):
    """业务操作响应"""
    success: bool = Field(..., description="操作是否成功")
    message: str = Field(..., description="操作结果消息")
    order: Optional[OrderResponse] = Field(None, description="订单信息")
