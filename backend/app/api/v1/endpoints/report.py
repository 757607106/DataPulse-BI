"""
报表查询和导出接口
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
import pandas as pd
from datetime import datetime

from app.services.vanna_service import vanna_service

router = APIRouter()

class ReportRequest(BaseModel):
    """报表请求模型"""
    dimensions: List[str] = []  # 维度字段
    metrics: List[str] = []     # 指标字段
    filters: Dict[str, Any] = {}  # 筛选条件
    group_by: List[str] = []     # 分组字段
    order_by: Optional[str] = None
    limit: Optional[int] = 1000

class ExportRequest(BaseModel):
    """导出请求模型"""
    report_request: ReportRequest
    format: str = "xlsx"  # xlsx, csv

@router.post("/query")
async def query_report(request: ReportRequest):
    """
    通用报表查询接口

    支持多维度筛选、分组汇总等功能
    """
    try:
        # 构建查询 SQL
        sql = vanna_service.build_report_sql(request)

        # 执行查询
        data = await vanna_service.execute_sql(sql)

        # 计算汇总数据
        summary = vanna_service.calculate_summary(data, request.metrics)

        return {
            "data": data,
            "summary": summary,
            "total_count": len(data),
            "sql": sql
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"报表查询失败: {str(e)}")

@router.post("/export")
async def export_report(request: ExportRequest):
    """
    导出报表数据

    支持 Excel 和 CSV 格式导出
    """
    try:
        # 先查询数据
        query_result = await query_report(request.report_request)

        # 转换为 DataFrame
        df = pd.DataFrame(query_result["data"])

        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{timestamp}.{request.format}"

        # 保存文件
        if request.format == "xlsx":
            df.to_excel(filename, index=False)
        elif request.format == "csv":
            df.to_csv(filename, index=False, encoding='utf-8-sig')
        else:
            raise HTTPException(status_code=400, detail="不支持的导出格式")

        # 返回文件
        return FileResponse(
            filename,
            media_type='application/octet-stream',
            filename=filename
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")

@router.get("/dashboard")
async def get_dashboard_data():
    """
    获取仪表板基础数据

    返回 KPI 指标和基础图表数据
    """
    try:
        # 获取关键指标
        kpis = await vanna_service.get_dashboard_kpis()

        # 获取基础图表数据
        charts = await vanna_service.get_dashboard_charts()

        return {
            "kpis": kpis,
            "charts": charts,
            "last_updated": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取仪表板数据失败: {str(e)}")
