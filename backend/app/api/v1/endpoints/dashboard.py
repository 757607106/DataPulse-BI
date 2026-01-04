"""
Dashboard 仪表盘接口
"""
from typing import List, Dict, Any
from decimal import Decimal
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
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
async def get_dashboard_overview(db: AsyncSession = Depends(get_db)):
    """
    获取 Dashboard 总览数据
    
    包含:
    - KPI 指标: 本月销售额、毛利、订单数
    - 销售趋势: 过去 30 天的销售额和毛利
    - 库存预警: 库存不足的前 5 个商品
    - 资金状况: 应收应付账款总额
    """
    try:
        # ===== 1. 查询 KPI 数据 (本月) =====
        kpi_sql = text("""
            SELECT 
                COALESCE(SUM(sales_amount), 0) as total_sales,
                COALESCE(SUM(gross_profit), 0) as gross_profit,
                COUNT(DISTINCT order_id) as order_count
            FROM view_bi_sales_analysis
            WHERE EXTRACT(YEAR FROM order_date) = EXTRACT(YEAR FROM CURRENT_DATE)
                AND EXTRACT(MONTH FROM order_date) = EXTRACT(MONTH FROM CURRENT_DATE)
                AND order_status IN ('confirmed', 'completed')
        """)
        
        kpi_result = await db.execute(kpi_sql)
        kpi_row = kpi_result.fetchone()
        
        total_sales = kpi_row[0] if kpi_row else Decimal('0')
        gross_profit = kpi_row[1] if kpi_row else Decimal('0')
        order_count = kpi_row[2] if kpi_row else 0
        
        # 计算毛利率
        gross_profit_rate = None
        if total_sales and total_sales > 0:
            gross_profit_rate = float((gross_profit / total_sales) * 100)
        
        kpi_data = KPIData(
            total_sales=total_sales,
            gross_profit=gross_profit,
            order_count=order_count,
            gross_profit_rate=gross_profit_rate
        )
        
        # ===== 2. 查询销售趋势 (过去 30 天) =====
        trend_sql = text("""
            SELECT 
                TO_CHAR(order_date, 'YYYY-MM-DD') as date_str,
                COALESCE(SUM(sales_amount), 0) as sales,
                COALESCE(SUM(gross_profit), 0) as profit
            FROM view_bi_sales_analysis
            WHERE order_date >= CURRENT_DATE - INTERVAL '30 days'
                AND order_status IN ('confirmed', 'completed')
            GROUP BY order_date
            ORDER BY order_date ASC
        """)
        
        trend_result = await db.execute(trend_sql)
        trend_rows = trend_result.fetchall()
        
        trends = [
            TrendPoint(
                date=row[0],
                sales=decimal_to_float(row[1]),
                profit=decimal_to_float(row[2])
            )
            for row in trend_rows
        ]
        
        # ===== 3. 查询库存预警 (库存不足的前 5 个商品) =====
        inventory_sql = text("""
            SELECT 
                product_name,
                current_stock,
                min_stock,
                warehouse_name,
                stock_status
            FROM view_bi_inventory_alert
            WHERE stock_status IN ('缺货', '库存不足')
            ORDER BY 
                CASE stock_status
                    WHEN '缺货' THEN 1
                    WHEN '库存不足' THEN 2
                    ELSE 3
                END,
                current_stock ASC
            LIMIT 5
        """)
        
        inventory_result = await db.execute(inventory_sql)
        inventory_rows = inventory_result.fetchall()
        
        inventory_alerts = [
            InventoryAlert(
                product_name=row[0],
                current_stock=decimal_to_float(row[1]),
                min_stock=decimal_to_float(row[2]) if row[2] else None,
                warehouse_name=row[3],
                stock_status=row[4]
            )
            for row in inventory_rows
        ]
        
        # ===== 4. 查询资金状况 =====
        # 应收账款总额
        receivable_sql = text("""
            SELECT COALESCE(SUM(current_balance), 0) as total_receivable
            FROM view_bi_finance_monitor
            WHERE record_type = 'receivable'
                AND current_balance > 0
        """)
        
        receivable_result = await db.execute(receivable_sql)
        receivable_row = receivable_result.fetchone()
        total_receivable = receivable_row[0] if receivable_row else Decimal('0')
        
        # 应付账款总额
        payable_sql = text("""
            SELECT COALESCE(SUM(current_balance), 0) as total_payable
            FROM view_bi_finance_monitor
            WHERE record_type = 'payable'
                AND current_balance > 0
        """)
        
        payable_result = await db.execute(payable_sql)
        payable_row = payable_result.fetchone()
        total_payable = payable_row[0] if payable_row else Decimal('0')
        
        # 本月费用总额
        expense_sql = text("""
            SELECT COALESCE(SUM(trans_amount), 0) as total_expense
            FROM view_bi_finance_monitor
            WHERE record_type = 'expense'
                AND EXTRACT(YEAR FROM trans_date) = EXTRACT(YEAR FROM CURRENT_DATE)
                AND EXTRACT(MONTH FROM trans_date) = EXTRACT(MONTH FROM CURRENT_DATE)
        """)
        
        expense_result = await db.execute(expense_sql)
        expense_row = expense_result.fetchone()
        total_expense = expense_row[0] if expense_row else Decimal('0')
        
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
async def get_kpi(db: AsyncSession = Depends(get_db)):
    """
    单独获取 KPI 数据
    """
    try:
        sql = text("""
            SELECT 
                COALESCE(SUM(sales_amount), 0) as total_sales,
                COALESCE(SUM(gross_profit), 0) as gross_profit,
                COUNT(DISTINCT order_id) as order_count
            FROM view_bi_sales_analysis
            WHERE EXTRACT(YEAR FROM order_date) = EXTRACT(YEAR FROM CURRENT_DATE)
                AND EXTRACT(MONTH FROM order_date) = EXTRACT(MONTH FROM CURRENT_DATE)
                AND order_status IN ('confirmed', 'completed')
        """)
        
        result = await db.execute(sql)
        row = result.fetchone()
        
        total_sales = row[0] if row else Decimal('0')
        gross_profit = row[1] if row else Decimal('0')
        order_count = row[2] if row else 0
        
        gross_profit_rate = None
        if total_sales and total_sales > 0:
            gross_profit_rate = float((gross_profit / total_sales) * 100)
        
        return {
            "total_sales": float(total_sales),
            "gross_profit": float(gross_profit),
            "order_count": order_count,
            "gross_profit_rate": gross_profit_rate
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"KPI 查询失败: {str(e)}")
