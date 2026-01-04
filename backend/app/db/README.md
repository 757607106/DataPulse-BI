# 进销存 BI 系统 - 数据库模型设计文档

## 📋 概述

本数据库模型专为**多维度 OLAP 分析**和**AI 自然语言查询**设计，支持以下核心分析维度：
- 🏢 **组织维度**：分公司、部门、业务员
- 🌍 **地理维度**：地区（华东、华北、华南等）
- 👥 **客户维度**：往来单位（客户/供应商）
- 📦 **商品维度**：商品分类、商品名称
- 🏪 **仓库维度**：仓库位置

## 🗂️ 文件结构

```
backend/app/
├── models/
│   └── bi_schema.py          # SQLAlchemy 模型定义（维度表 + 事实表）
└── db/
    ├── init_db.py            # 数据库初始化脚本
    └── init_views.sql        # AI 专用宽表视图 SQL
```

## 📊 数据模型架构

### 1️⃣ 维度表 (Dimension Tables)

| 表名 | 说明 | 关键字段 |
|------|------|----------|
| `sys_department` | 组织架构（分公司+部门） | `company_name`（关键维度）, `name`, `parent_id` |
| `sys_employee` | 员工（业务员） | `name`（业务员维度）, `dept_id` |
| `base_partner` | 往来单位 | `name`, `type`(客户/供应商), `region`（关键维度） |
| `base_warehouse` | 仓库 | `name`, `location` |
| `base_product` | 商品 | `name`, `category`（关键维度）, `cost_price`（用于毛利计算） |

### 2️⃣ 事实表 (Fact Tables)

| 表名 | 说明 | 核心指标 |
|------|------|----------|
| `biz_order` | 订单主表 | `type`(销售/采购), `total_amount`, `order_date` |
| `biz_order_item` | 订单明细 | `quantity`, `price`, `subtotal` |
| `fact_finance` | 财务流水（应收/应付/费用） | `type`, `amount`, `balance`, `expense_category` |
| `inv_current_stock` | 实时库存 | `quantity` |

### 3️⃣ AI 分析视图 (AI Analysis Views)

| 视图名 | 用途 | 核心指标 |
|--------|------|----------|
| `view_bi_sales_analysis` | 销售毛利全景分析 | 销售额、成本、毛利、毛利率 |
| `view_bi_finance_monitor` | 资金费用综合监控 | 应收应付余额、费用支出 |
| `view_bi_inventory_alert` | 库存预警分析 | 库存数量、预警状态、库存价值 |
| `view_bi_purchase_analysis` | 采购分析 | 采购金额、采购数量 |

## 🚀 快速开始

### 1. 安装依赖

```bash
cd backend
pip install sqlalchemy psycopg2-binary  # PostgreSQL
# 或
pip install sqlalchemy pymysql  # MySQL
```

### 2. 配置数据库连接

在 `backend/app/core/config.py` 中配置：

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:password@localhost/datapulse_bi"
    # 或 MySQL: "mysql+pymysql://user:password@localhost/datapulse_bi"

settings = Settings()
```

### 3. 初始化数据库

```bash
cd backend

# 仅创建表和视图
python -m app.db.init_db

# 创建表、视图和示例数据
python -m app.db.init_db --sample

# 删除现有表后重新创建（谨慎！）
python -m app.db.init_db --drop
```

## 💡 使用示例

### Python 代码中使用模型

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.bi_schema import (
    SysDepartment, SysEmployee, BasePartner, 
    BaseProduct, BizOrder, BizOrderItem
)
from app.core.config import settings

# 创建数据库会话
engine = create_engine(settings.DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# 查询示例：获取北京分公司的销售部门
dept = session.query(SysDepartment).filter(
    SysDepartment.company_name == "北京分公司",
    SysDepartment.name == "销售部"
).first()

# 查询示例：获取某业务员的所有销售订单
orders = session.query(BizOrder).filter(
    BizOrder.salesman_id == 1,
    BizOrder.type == "sales"
).all()
```

### AI 可以直接查询视图

```sql
-- 问题："2024年华东地区的销售额和毛利是多少？"
SELECT 
    SUM(sales_amount) as total_sales,
    SUM(gross_profit) as total_profit
FROM view_bi_sales_analysis
WHERE year = 2024 
    AND region = '华东';

-- 问题："张三业务员在电子产品类的毛利率是多少？"
SELECT 
    salesman_name,
    category,
    SUM(sales_amount) as sales,
    SUM(gross_profit) as profit,
    AVG(gross_profit_rate) as avg_profit_rate
FROM view_bi_sales_analysis
WHERE salesman_name = '张三' 
    AND category = '电子产品'
GROUP BY salesman_name, category;

-- 问题："北京分公司本月的费用总额是多少？"
SELECT 
    company_name,
    expense_category,
    SUM(trans_amount) as total_expense
FROM view_bi_finance_monitor
WHERE company_name = '北京分公司'
    AND record_type = 'expense'
    AND year = 2024 AND month = 1
GROUP BY company_name, expense_category;
```

## 🎯 核心设计亮点

### 1. 所有字段包含 `comment` 参数
每个字段都有清晰的业务含义注释，便于 AI 理解：
```python
company_name: Mapped[str] = mapped_column(
    String(100),
    nullable=False,
    index=True,
    comment="所属分公司名称（关键分析维度）"  # 👈 AI 可识别
)
```

### 2. 视图完全扁平化
AI 无需理解复杂的 JOIN 逻辑，所有维度已铺平：
- ✅ `view_bi_sales_analysis` 包含：公司、部门、业务员、地区、客户、商品等所有维度
- ✅ 核心指标已预计算：毛利、毛利率、库存价值等

### 3. 混合事实表设计
`fact_finance` 统一管理应收、应付、费用三类财务数据：
```python
type: Mapped[FinanceRecordType] = mapped_column(
    Enum(FinanceRecordType),
    comment="记录类型：receivable应收/payable应付/expense费用"
)
```

### 4. 时间维度自动拆分
视图中自动提取 `year`, `month`，便于时间序列分析：
```sql
EXTRACT(YEAR FROM o.order_date) AS year,
EXTRACT(MONTH FROM o.order_date) AS month,
```

## 📈 支持的分析场景

### ✅ 销售分析
- 按分公司、部门、业务员统计销售额和毛利
- 按地区、客户、商品分类分析销售趋势
- 计算毛利率、同比环比增长

### ✅ 财务分析
- 应收账款、应付账款余额统计
- 费用支出分析（按科目、部门、时间）
- 资金流动性监控

### ✅ 库存分析
- 库存预警（低于最低库存线）
- 库存价值统计
- 滞销商品识别

### ✅ 采购分析
- 供应商采购金额排名
- 采购价格趋势分析
- 采购员绩效评估

## ⚠️ 注意事项

1. **生产环境建议**：
   - 对高频查询字段创建索引（见 `init_views.sql` 底部的索引建议）
   - 定期更新统计信息以优化查询计划
   - 对视图创建物化视图以提升性能

2. **数据一致性**：
   - `BizOrderItem.subtotal` 应由应用层计算：`quantity * price`
   - `BizOrder.total_amount` 应为所有明细的 `subtotal` 之和
   - 建议使用数据库触发器或应用层逻辑确保一致性

3. **AI 训练建议**：
   - 使用 Vanna AI 时，先用视图字段的 `comment` 训练模型
   - 提供典型的自然语言问题和对应的 SQL 查询作为训练样本

## 🔧 维护与扩展

### 添加新维度
1. 在 `bi_schema.py` 中定义新的维度表
2. 在事实表中添加外键关联
3. 更新相关视图，将新维度字段铺平

### 添加新指标
1. 在视图的 `SELECT` 子句中添加计算逻辑
2. 为新指标字段添加清晰的别名和注释

### 性能优化
```sql
-- 为高频查询字段创建索引
CREATE INDEX idx_order_date_type ON biz_order(order_date, type);
CREATE INDEX idx_finance_date_type ON fact_finance(trans_date, type);

-- 创建物化视图（PostgreSQL）
CREATE MATERIALIZED VIEW mv_bi_sales_analysis AS
SELECT * FROM view_bi_sales_analysis;

-- 定期刷新物化视图
REFRESH MATERIALIZED VIEW mv_bi_sales_analysis;
```

## 📞 支持

如有问题或建议，请联系开发团队。

---

**版本**: 1.0.0  
**最后更新**: 2026-01-05
