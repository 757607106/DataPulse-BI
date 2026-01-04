"""
Dashboard 数据模型
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import date
from decimal import Decimal


class KPIData(BaseModel):
    """KPI 指标数据"""
    total_sales: Decimal = Field(description="本月销售总额")
    gross_profit: Decimal = Field(description="本月毛利")
    order_count: int = Field(description="本月订单数")
    gross_profit_rate: Optional[float] = Field(None, description="毛利率(%)")


class TrendPoint(BaseModel):
    """趋势图数据点"""
    date: str = Field(description="日期")
    sales: float = Field(description="销售额")
    profit: float = Field(description="毛利")


class InventoryAlert(BaseModel):
    """库存预警数据"""
    product_name: str = Field(description="商品名称")
    current_stock: float = Field(description="当前库存")
    min_stock: Optional[float] = Field(None, description="最低库存")
    warehouse_name: str = Field(description="仓库名称")
    stock_status: str = Field(description="库存状态")


class FinanceStatus(BaseModel):
    """资金状况数据"""
    total_receivable: Decimal = Field(description="应收账款总额")
    total_payable: Decimal = Field(description="应付账款总额")
    total_expense: Decimal = Field(description="本月费用总额")


class DashboardOverview(BaseModel):
    """Dashboard 总览数据"""
    kpi: KPIData = Field(description="KPI 指标")
    trends: List[TrendPoint] = Field(description="销售趋势(30天)")
    inventory_alerts: List[InventoryAlert] = Field(description="库存预警(前5)")
    finance_status: FinanceStatus = Field(description="资金状况")
