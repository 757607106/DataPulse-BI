"""
报表相关的 Pydantic 模型
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

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

class DashboardData(BaseModel):
    """仪表板数据模型"""
    kpis: Dict[str, Any]
    charts: List[Dict[str, Any]]
    last_updated: str

class ReportSummary(BaseModel):
    """报表汇总模型"""
    total_count: int
    summary: Dict[str, Any]
    data: List[Dict[str, Any]]
    sql: str
