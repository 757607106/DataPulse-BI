"""
进销存 BI 系统核心数据模型
支持多维度 OLAP 分析：分公司、部门、业务员、仓库、往来单位、地区、商品
所有字段包含 comment 参数以支持 AI 自然语言识别
"""
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from enum import Enum as PyEnum

from sqlalchemy import (
    String, Integer, Numeric, DateTime, Date, ForeignKey, Enum, Text
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """基础模型类"""
    pass


# ==================== 枚举类型定义 ====================

class PartnerType(str, PyEnum):
    """往来单位类型"""
    CUSTOMER = "customer"  # 客户
    SUPPLIER = "supplier"  # 供应商


class OrderType(str, PyEnum):
    """订单类型"""
    SALES = "sales"  # 销售订单
    PURCHASE = "purchase"  # 采购订单


class OrderStatus(str, PyEnum):
    """订单状态"""
    DRAFT = "draft"  # 草稿
    CONFIRMED = "confirmed"  # 已确认
    COMPLETED = "completed"  # 已完成
    CANCELLED = "cancelled"  # 已取消


class FinanceRecordType(str, PyEnum):
    """财务记录类型"""
    RECEIVABLE = "receivable"  # 应收账款
    PAYABLE = "payable"  # 应付账款
    EXPENSE = "expense"  # 费用支出


# ==================== 维度表 ====================

class SysUser(Base):
    """用户表 - 用于JWT认证"""
    __tablename__ = "sys_user"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="用户ID"
    )
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="用户名"
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="哈希密码"
    )
    role: Mapped[str] = mapped_column(
        String(20),
        default="user",
        comment="角色：admin管理员/user普通用户"
    )
    is_active: Mapped[bool] = mapped_column(
        default=True,
        comment="是否激活"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间"
    )


class SysDepartment(Base):
    """组织架构维度表 - 支持分公司和部门两级结构"""
    __tablename__ = "sys_department"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="部门ID"
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="部门名称"
    )
    company_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="所属分公司名称（关键分析维度）"
    )
    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("sys_department.id"),
        nullable=True,
        comment="上级部门ID"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        comment="创建时间"
    )

    # 关系定义
    parent: Mapped[Optional["SysDepartment"]] = relationship(
        "SysDepartment",
        remote_side=[id],
        back_populates="children"
    )
    children: Mapped[List["SysDepartment"]] = relationship(
        "SysDepartment",
        back_populates="parent"
    )
    employees: Mapped[List["SysEmployee"]] = relationship(
        "SysEmployee",
        back_populates="department"
    )
    finance_records: Mapped[List["FactFinance"]] = relationship(
        "FactFinance",
        back_populates="department"
    )


class SysEmployee(Base):
    """人员维度表 - 业务员是关键分析维度"""
    __tablename__ = "sys_employee"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="员工ID"
    )
    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="员工姓名（业务员维度）"
    )
    dept_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("sys_department.id"),
        nullable=False,
        comment="所属部门ID"
    )
    email: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="邮箱"
    )
    phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="联系电话"
    )
    is_active: Mapped[bool] = mapped_column(
        default=True,
        comment="是否在职"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        comment="创建时间"
    )

    # 关系定义
    department: Mapped["SysDepartment"] = relationship(
        "SysDepartment",
        back_populates="employees"
    )
    orders: Mapped[List["BizOrder"]] = relationship(
        "BizOrder",
        back_populates="salesman"
    )
    finance_records: Mapped[List["FactFinance"]] = relationship(
        "FactFinance",
        back_populates="salesman"
    )


class BasePartner(Base):
    """往来单位维度表 - 客户/供应商"""
    __tablename__ = "base_partner"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="往来单位ID"
    )
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
        comment="往来单位名称"
    )
    type: Mapped[PartnerType] = mapped_column(
        Enum(PartnerType),
        nullable=False,
        comment="类型：customer客户/supplier供应商"
    )
    region: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="所属地区（关键分析维度：华东/华北/华南等）"
    )
    contact_person: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="联系人"
    )
    phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="联系电话"
    )
    address: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
        comment="地址"
    )
    credit_limit: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2),
        nullable=True,
        comment="信用额度"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        comment="创建时间"
    )

    # 关系定义
    orders: Mapped[List["BizOrder"]] = relationship(
        "BizOrder",
        back_populates="partner"
    )
    finance_records: Mapped[List["FactFinance"]] = relationship(
        "FactFinance",
        back_populates="partner"
    )


class BaseWarehouse(Base):
    """仓库维度表"""
    __tablename__ = "base_warehouse"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="仓库ID"
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="仓库名称"
    )
    location: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="仓库位置"
    )
    manager: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="仓库管理员"
    )
    is_active: Mapped[bool] = mapped_column(
        default=True,
        comment="是否启用"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        comment="创建时间"
    )

    # 关系定义
    orders: Mapped[List["BizOrder"]] = relationship(
        "BizOrder",
        back_populates="warehouse"
    )
    stock_records: Mapped[List["InvCurrentStock"]] = relationship(
        "InvCurrentStock",
        back_populates="warehouse"
    )


class BaseProduct(Base):
    """商品维度表"""
    __tablename__ = "base_product"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="商品ID"
    )
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
        comment="商品名称"
    )
    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="商品分类（关键分析维度）"
    )
    specification: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="规格型号"
    )
    unit: Mapped[str] = mapped_column(
        String(20),
        default="件",
        comment="计量单位"
    )
    cost_price: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False,
        comment="成本价（用于计算毛利）"
    )
    min_stock: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2),
        nullable=True,
        comment="最低库存预警线"
    )
    is_active: Mapped[bool] = mapped_column(
        default=True,
        comment="是否启用"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        comment="创建时间"
    )

    # 关系定义
    order_items: Mapped[List["BizOrderItem"]] = relationship(
        "BizOrderItem",
        back_populates="product"
    )
    stock_records: Mapped[List["InvCurrentStock"]] = relationship(
        "InvCurrentStock",
        back_populates="product"
    )


# ==================== 事实表 ====================

class BizOrder(Base):
    """订单主表 - 销售/采购订单"""
    __tablename__ = "biz_order"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="订单ID"
    )
    order_no: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="订单编号"
    )
    type: Mapped[OrderType] = mapped_column(
        Enum(OrderType),
        nullable=False,
        index=True,
        comment="订单类型：sales销售/purchase采购"
    )
    order_date: Mapped[datetime] = mapped_column(
        Date,
        nullable=False,
        index=True,
        comment="订单日期"
    )
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus),
        default=OrderStatus.DRAFT,
        comment="订单状态"
    )
    salesman_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("sys_employee.id"),
        nullable=False,
        comment="业务员ID（关键分析维度）"
    )
    partner_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("base_partner.id"),
        nullable=False,
        comment="往来单位ID（客户或供应商）"
    )
    warehouse_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("base_warehouse.id"),
        nullable=False,
        comment="仓库ID"
    )
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        default=0,
        comment="订单总金额"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="备注"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间"
    )

    # 关系定义
    salesman: Mapped["SysEmployee"] = relationship(
        "SysEmployee",
        back_populates="orders"
    )
    partner: Mapped["BasePartner"] = relationship(
        "BasePartner",
        back_populates="orders"
    )
    warehouse: Mapped["BaseWarehouse"] = relationship(
        "BaseWarehouse",
        back_populates="orders"
    )
    items: Mapped[List["BizOrderItem"]] = relationship(
        "BizOrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )


class BizOrderItem(Base):
    """订单明细表"""
    __tablename__ = "biz_order_item"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="明细ID"
    )
    order_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("biz_order.id"),
        nullable=False,
        comment="订单ID"
    )
    product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("base_product.id"),
        nullable=False,
        comment="商品ID"
    )
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False,
        comment="数量"
    )
    price: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False,
        comment="成交单价"
    )
    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False,
        comment="小计金额（数量*单价）"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
        comment="备注"
    )

    # 关系定义
    order: Mapped["BizOrder"] = relationship(
        "BizOrder",
        back_populates="items"
    )
    product: Mapped["BaseProduct"] = relationship(
        "BaseProduct",
        back_populates="order_items"
    )


class FactFinance(Base):
    """财务流水事实表 - 统一管理应收/应付/费用"""
    __tablename__ = "fact_finance"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="记录ID"
    )
    type: Mapped[FinanceRecordType] = mapped_column(
        Enum(FinanceRecordType),
        nullable=False,
        index=True,
        comment="记录类型：receivable应收/payable应付/expense费用"
    )
    trans_date: Mapped[datetime] = mapped_column(
        Date,
        nullable=False,
        index=True,
        comment="业务发生日期"
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False,
        comment="发生金额（正数表示增加，负数表示减少）"
    )
    balance: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2),
        nullable=True,
        comment="当前余额（仅应收应付有效）"
    )
    expense_category: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        index=True,
        comment="费用科目（仅type=expense时有效，如差旅费、房租等）"
    )
    partner_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("base_partner.id"),
        nullable=True,
        comment="往来单位ID（应收应付时使用）"
    )
    dept_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("sys_department.id"),
        nullable=False,
        comment="归属部门ID"
    )
    salesman_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("sys_employee.id"),
        nullable=True,
        comment="经办业务员ID"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="业务描述"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        comment="创建时间"
    )

    # 关系定义
    partner: Mapped[Optional["BasePartner"]] = relationship(
        "BasePartner",
        back_populates="finance_records"
    )
    department: Mapped["SysDepartment"] = relationship(
        "SysDepartment",
        back_populates="finance_records"
    )
    salesman: Mapped[Optional["SysEmployee"]] = relationship(
        "SysEmployee",
        back_populates="finance_records"
    )


class InvCurrentStock(Base):
    """实时库存表"""
    __tablename__ = "inv_current_stock"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="记录ID"
    )
    warehouse_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("base_warehouse.id"),
        nullable=False,
        comment="仓库ID"
    )
    product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("base_product.id"),
        nullable=False,
        comment="商品ID"
    )
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        default=0,
        comment="当前库存数量"
    )
    last_updated: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment="最后更新时间"
    )

    # 关系定义
    warehouse: Mapped["BaseWarehouse"] = relationship(
        "BaseWarehouse",
        back_populates="stock_records"
    )
    product: Mapped["BaseProduct"] = relationship(
        "BaseProduct",
        back_populates="stock_records"
    )

    # 联合唯一约束
    __table_args__ = (
        {"comment": "实时库存表（仓库+商品唯一）"},
    )
