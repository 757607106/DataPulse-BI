"""
Pydantic 模型定义
"""
from .chat import *
from .report import *
from .dashboard import *
from .auth import *
from .business import *

__all__ = [
    # Chat
    "ChatRequest", 
    "ChatResponse",
    # Report
    "ReportRequest", 
    "ExportRequest",
    # Dashboard
    "DashboardOverview",
    "KPIData",
    "TrendPoint",
    "InventoryAlert",
    "FinanceStatus",
    # Auth
    "Token",
    "TokenData",
    "LoginRequest",
    "UserBase",
    "UserResponse",
    "UserCreate",
    # Business
    "ProductCreate",
    "ProductResponse",
    "OrderItemCreate",
    "InboundRequest",
    "OutboundRequest",
    "OrderItemResponse",
    "OrderResponse",
    "BusinessOperationResponse",
]
