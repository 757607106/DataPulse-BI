"""
进销存 BI 系统 - FastAPI 后端服务入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import chat, report, dashboard
from app.core.config import settings

# 导入数据库模型（可在 API 路由中使用）
from app.models.bi_schema import (
    # 维度表
    SysDepartment, SysEmployee, BasePartner, BaseWarehouse, BaseProduct,
    # 事实表
    BizOrder, BizOrderItem, FactFinance, InvCurrentStock,
    # 枚举类型
    PartnerType, OrderType, OrderStatus, FinanceRecordType
)

# 创建 FastAPI 应用实例
app = FastAPI(
    title="进销存 BI 系统",
    description="基于 AI 的智能商业智能分析系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # 前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(report.router, prefix="/api/v1/report", tags=["report"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])

@app.get("/")
async def root():
    """根路径"""
    return {"message": "进销存 BI 系统 API", "status": "running"}

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}
