"""
数据模型模块
"""
from .base import Base
from .bi_schema import (
    # 维度表
    SysUser,
    SysDepartment,
    SysEmployee,
    BasePartner,
    BaseWarehouse,
    BaseProduct,
    # 事实表
    BizOrder,
    BizOrderItem,
    FactFinance,
    InvCurrentStock,
    # 枚举类型
    PartnerType,
    OrderType,
    OrderStatus,
    FinanceRecordType,
)

__all__ = [
    "Base",
    # 维度表
    "SysUser",
    "SysDepartment",
    "SysEmployee",
    "BasePartner",
    "BaseWarehouse",
    "BaseProduct",
    # 事实表
    "BizOrder",
    "BizOrderItem",
    "FactFinance",
    "InvCurrentStock",
    # 枚举类型
    "PartnerType",
    "OrderType",
    "OrderStatus",
    "FinanceRecordType",
]
