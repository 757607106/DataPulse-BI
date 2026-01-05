"""
Dashboard 仪表盘接口 - 基于 ORM 模型直接查询
"""
from typing import List, Dict, Any, Annotated
from decimal import Decimal
from datetime import datetime, timedelta, date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func, and_, or_, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import get_current_active_user
from app.db.session import get_db
from app.models.bi_schema import (
    SysUser,
    BizOrder,
    BizOrderItem,
    BaseProduct,
    InvCurrentStock,
    BaseWarehouse,
    FactFinance,
    OrderType,
    OrderStatus,
    FinanceRecordType
)
from app.schemas.dashboard import (
    DashboardOverview, 
    KPIData, 
    TrendPoint, 
    InventoryAlert, 
    FinanceStatus
)

router = APIRouter()


def decimal_to_float(value: Any) -> float:
    """将 Decimal 转换为 float"""
    if isinstance(value, Decimal):
        return float(value)
    return value


@router.get("/overview", response_model=DashboardOverview)
async def get_dashboard_overview(
    current_user: Annotated[SysUser, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    获取 Dashboard 总览数据（需要认证）
    
    包含:
    - KPI 指标: 本月销售额、毛利估算、订单数
    - 销售趋势: 过去 30 天的每日销售额
    - 库存预警: 库存不足的商品列表（前 10 个）
    - 资金状况: 应收应付账款总额
    """
    try:
        # 获取本月日期范围
        today = date.today()
        first_day_of_month = today.replace(day=1)
        
        # 获取过去 30 天日期范围
        thirty_days_ago = today - timedelta(days=30)
        
        # ===== 1. 查询 KPI 数据 (本月) =====
        # 本月销售订单总额
        sales_result = await db.execute(
            select(func.coalesce(func.sum(BizOrder.total_amount), 0))
            .where(
                and_(
                    BizOrder.type == OrderType.SALES,
                    BizOrder.order_date >= first_day_of_month,
                    BizOrder.status.in_([OrderStatus.CONFIRMED, OrderStatus.COMPLETED])
                )
            )
        )
        total_sales = sales_result.scalar() or Decimal('0')
        
        # 本月订单数
        order_count_result = await db.execute(
            select(func.count(BizOrder.id))
            .where(
                and_(
                    BizOrder.type == OrderType.SALES,
                    BizOrder.order_date >= first_day_of_month,
                    BizOrder.status.in_([OrderStatus.CONFIRMED, OrderStatus.COMPLETED])
                )
            )
        )
        order_count = order_count_result.scalar() or 0
        
        # 估算毛利：销售额 - 成本
        # 成本 = SUM(订单明细数量 * 商品成本价)
        profit_result = await db.execute(
            select(
                func.coalesce(
                    func.sum(
                        BizOrderItem.quantity * BaseProduct.cost_price
                    ),
                    0
                )
            )
            .select_from(BizOrder)
            .join(BizOrderItem, BizOrderItem.order_id == BizOrder.id)
            .join(BaseProduct, BaseProduct.id == BizOrderItem.product_id)
            .where(
                and_(
                    BizOrder.type == OrderType.SALES,
                    BizOrder.order_date >= first_day_of_month,
                    BizOrder.status.in_([OrderStatus.CONFIRMED, OrderStatus.COMPLETED])
                )
            )
        )
        total_cost = profit_result.scalar() or Decimal('0')
        gross_profit = total_sales - total_cost
        
        # 计算毛利率
        gross_profit_rate = None
        if total_sales > 0:
            gross_profit_rate = float((gross_profit / total_sales) * 100)
        
        kpi_data = KPIData(
            total_sales=total_sales,
            gross_profit=gross_profit,
            order_count=order_count,
            gross_profit_rate=gross_profit_rate
        )
        
        # ===== 2. 查询销售趋势 (过去 30 天) =====
        # 按日期分组统计销售额
        trend_result = await db.execute(
            select(
                func.to_char(BizOrder.order_date, 'YYYY-MM-DD').label('date_str'),
                func.coalesce(func.sum(BizOrder.total_amount), 0).label('sales')
            )
            .where(
                and_(
                    BizOrder.type == OrderType.SALES,
                    BizOrder.order_date >= thirty_days_ago,
                    BizOrder.status.in_([OrderStatus.CONFIRMED, OrderStatus.COMPLETED])
                )
            )
            .group_by(BizOrder.order_date)
            .order_by(BizOrder.order_date.asc())
        )
        trend_rows = trend_result.fetchall()
        
        trends = [
            TrendPoint(
                date=row.date_str,
                sales=decimal_to_float(row.sales),
                profit=decimal_to_float(row.sales * Decimal('0.2'))  # 简化：假设毛利率 20%
            )
            for row in trend_rows
        ]
        
        # ===== 3. 查询库存预警 (库存不足的商品) =====
        # 联查库存和商品信息，筛选 quantity < min_stock
        inventory_result = await db.execute(
            select(
                BaseProduct.name.label('product_name'),
                InvCurrentStock.quantity.label('current_stock'),
                BaseProduct.min_stock.label('min_stock'),
                BaseWarehouse.name.label('warehouse_name')
            )
            .select_from(InvCurrentStock)
            .join(BaseProduct, BaseProduct.id == InvCurrentStock.product_id)
            .join(BaseWarehouse, BaseWarehouse.id == InvCurrentStock.warehouse_id)
            .where(
                and_(
                    BaseProduct.min_stock.isnot(None),
                    InvCurrentStock.quantity < BaseProduct.min_stock
                )
            )
            .order_by(InvCurrentStock.quantity.asc())
            .limit(10)
        )
        inventory_rows = inventory_result.fetchall()
        
        inventory_alerts = [
            InventoryAlert(
                product_name=row.product_name,
                current_stock=decimal_to_float(row.current_stock),
                min_stock=decimal_to_float(row.min_stock) if row.min_stock else None,
                warehouse_name=row.warehouse_name,
                stock_status="缺货" if row.current_stock == 0 else "库存不足"
            )
            for row in inventory_rows
        ]
        
        # ===== 4. 查询资金状况 =====
        # 应收账款总额（balance 字段存储当前余额）
        receivable_result = await db.execute(
            select(func.coalesce(func.sum(FactFinance.balance), 0))
            .where(
                and_(
                    FactFinance.type == FinanceRecordType.RECEIVABLE,
                    FactFinance.balance > 0
                )
            )
        )
        total_receivable = receivable_result.scalar() or Decimal('0')
        
        # 应付账款总额
        payable_result = await db.execute(
            select(func.coalesce(func.sum(FactFinance.balance), 0))
            .where(
                and_(
                    FactFinance.type == FinanceRecordType.PAYABLE,
                    FactFinance.balance > 0
                )
            )
        )
        total_payable = payable_result.scalar() or Decimal('0')
        
        # 本月费用总额
        expense_result = await db.execute(
            select(func.coalesce(func.sum(FactFinance.amount), 0))
            .where(
                and_(
                    FactFinance.type == FinanceRecordType.EXPENSE,
                    FactFinance.trans_date >= first_day_of_month
                )
            )
        )
        total_expense = expense_result.scalar() or Decimal('0')
        
        finance_status = FinanceStatus(
            total_receivable=total_receivable,
            total_payable=total_payable,
            total_expense=total_expense
        )
        
        # ===== 组装返回数据 =====
        return DashboardOverview(
            kpi=kpi_data,
            trends=trends,
            inventory_alerts=inventory_alerts,
            finance_status=finance_status
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Dashboard 数据查询失败: {str(e)}"
        )


@router.get("/kpi")
async def get_kpi(
    current_user: Annotated[SysUser, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    单独获取 KPI 数据（需要认证）
    """
    try:
        today = date.today()
        first_day_of_month = today.replace(day=1)
        
        # 本月销售总额
        sales_result = await db.execute(
            select(func.coalesce(func.sum(BizOrder.total_amount), 0))
            .where(
                and_(
                    BizOrder.type == OrderType.SALES,
                    BizOrder.order_date >= first_day_of_month,
                    BizOrder.status.in_([OrderStatus.CONFIRMED, OrderStatus.COMPLETED])
                )
            )
        )
        total_sales = sales_result.scalar() or Decimal('0')
        
        # 本月订单数
        order_count_result = await db.execute(
            select(func.count(BizOrder.id))
            .where(
                and_(
                    BizOrder.type == OrderType.SALES,
                    BizOrder.order_date >= first_day_of_month,
                    BizOrder.status.in_([OrderStatus.CONFIRMED, OrderStatus.COMPLETED])
                )
            )
        )
        order_count = order_count_result.scalar() or 0
        
        # 估算毛利
        profit_result = await db.execute(
            select(
                func.coalesce(
                    func.sum(BizOrderItem.quantity * BaseProduct.cost_price),
                    0
                )
            )
            .select_from(BizOrder)
            .join(BizOrderItem, BizOrderItem.order_id == BizOrder.id)
            .join(BaseProduct, BaseProduct.id == BizOrderItem.product_id)
            .where(
                and_(
                    BizOrder.type == OrderType.SALES,
                    BizOrder.order_date >= first_day_of_month,
                    BizOrder.status.in_([OrderStatus.CONFIRMED, OrderStatus.COMPLETED])
                )
            )
        )
        total_cost = profit_result.scalar() or Decimal('0')
        gross_profit = total_sales - total_cost
        
        gross_profit_rate = None
        if total_sales > 0:
            gross_profit_rate = float((gross_profit / total_sales) * 100)
        
        return {
            "total_sales": float(total_sales),
            "gross_profit": float(gross_profit),
            "order_count": order_count,
            "gross_profit_rate": gross_profit_rate
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"KPI 查询失败: {str(e)}")
