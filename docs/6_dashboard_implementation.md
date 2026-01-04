# Dashboard 后端实现详细文档

## 📋 文档概述

本文档详细记录了进销存 BI 系统 Dashboard 后端接口的实现过程，包括数据库会话管理、数据模型定义、API 接口实现、Vanna AI 服务集成以及路由注册等核心模块。

**实现日期**: 2026-01-05  
**技术栈**: FastAPI + SQLAlchemy (异步) + PostgreSQL + Vanna.ai  
**文档版本**: v1.0

---

## 🏗️ 架构设计

### 整体架构图

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Application                   │
├─────────────────────────────────────────────────────────┤
│  Router Layer (API Endpoints)                           │
│  ├─ /api/v1/dashboard/overview  ← 总览数据             │
│  ├─ /api/v1/dashboard/kpi       ← KPI 指标             │
│  └─ /api/v1/chat                ← AI 问答              │
├─────────────────────────────────────────────────────────┤
│  Service Layer                                           │
│  ├─ VannaService  ← AI SQL 生成、模型训练              │
│  └─ Dashboard Service (在 endpoint 中实现)              │
├─────────────────────────────────────────────────────────┤
│  Database Layer                                          │
│  ├─ Session Management (异步会话)                       │
│  ├─ ORM Models (SQLAlchemy)                             │
│  └─ Database Views (宽表视图)                           │
│      ├─ view_bi_sales_analysis      (销售分析)         │
│      ├─ view_bi_finance_monitor     (财务监控)         │
│      ├─ view_bi_inventory_alert     (库存预警)         │
│      └─ view_bi_purchase_analysis   (采购分析)         │
└─────────────────────────────────────────────────────────┘
```

### 技术选型理由

1. **异步数据库**: 使用 `asyncpg` 驱动提升并发性能
2. **宽表视图**: 为 AI 提供扁平化数据，避免复杂 JOIN
3. **Pydantic 模型**: 自动数据验证和 JSON 序列化
4. **依赖注入**: 使用 FastAPI Depends 管理数据库会话生命周期

---

## 📦 模块 1: 数据库会话管理

### 文件路径
```
backend/app/db/session.py
```

### 核心代码

```python
"""
数据库会话管理
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# 创建异步数据库引擎
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
    pool_pre_ping=True,  # 连接池预检查
)

# 创建异步会话工厂
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # 提交后不过期对象
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    数据库会话依赖
    
    使用示例:
        @router.get("/endpoint")
        async def endpoint(db: AsyncSession = Depends(get_db)):
            result = await db.execute(...)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

### 设计要点

| 配置项 | 说明 | 影响 |
|--------|------|------|
| `pool_pre_ping=True` | 连接前检查连接是否有效 | 避免使用失效连接 |
| `expire_on_commit=False` | 提交后对象不过期 | 可继续访问已提交对象属性 |
| `autocommit=False` | 手动控制事务 | 更精细的事务管理 |
| `autoflush=False` | 手动刷新 | 减少不必要的 SQL |

### 会话生命周期

```
Request ─┐
         ├─> get_db() 创建 session
         ├─> 执行业务逻辑
         ├─> 成功: commit()
         ├─> 异常: rollback()
         └─> 最终: close()
Response ─┘
```

---

## 📊 模块 2: Dashboard 数据模型

### 文件路径
```
backend/app/schemas/dashboard.py
```

### 数据模型设计

#### 2.1 KPIData - KPI 指标模型

```python
class KPIData(BaseModel):
    """KPI 指标数据"""
    total_sales: Decimal = Field(description="本月销售总额")
    gross_profit: Decimal = Field(description="本月毛利")
    order_count: int = Field(description="本月订单数")
    gross_profit_rate: Optional[float] = Field(None, description="毛利率(%)")
```

**业务逻辑**:
- `total_sales`: 本月已确认/已完成订单的销售额总和
- `gross_profit`: 本月毛利 = 销售额 - 成本
- `gross_profit_rate`: 毛利率(%) = (毛利 / 销售额) × 100

#### 2.2 TrendPoint - 趋势图数据点

```python
class TrendPoint(BaseModel):
    """趋势图数据点"""
    date: str = Field(description="日期")
    sales: float = Field(description="销售额")
    profit: float = Field(description="毛利")
```

**用途**: 用于 ECharts 折线图渲染 30 天销售趋势

#### 2.3 InventoryAlert - 库存预警模型

```python
class InventoryAlert(BaseModel):
    """库存预警数据"""
    product_name: str = Field(description="商品名称")
    current_stock: float = Field(description="当前库存")
    min_stock: Optional[float] = Field(None, description="最低库存")
    warehouse_name: str = Field(description="仓库名称")
    stock_status: str = Field(description="库存状态")
```

**库存状态说明**:
- `缺货`: `current_stock <= 0`
- `库存不足`: `current_stock < min_stock`
- `正常`: `min_stock <= current_stock < min_stock * 3`
- `库存充足`: `current_stock >= min_stock * 3`

#### 2.4 FinanceStatus - 资金状况模型

```python
class FinanceStatus(BaseModel):
    """资金状况数据"""
    total_receivable: Decimal = Field(description="应收账款总额")
    total_payable: Decimal = Field(description="应付账款总额")
    total_expense: Decimal = Field(description="本月费用总额")
```

#### 2.5 DashboardOverview - 总览聚合模型

```python
class DashboardOverview(BaseModel):
    """Dashboard 总览数据"""
    kpi: KPIData = Field(description="KPI 指标")
    trends: List[TrendPoint] = Field(description="销售趋势(30天)")
    inventory_alerts: List[InventoryAlert] = Field(description="库存预警(前5)")
    finance_status: FinanceStatus = Field(description="资金状况")
```

### 模型关系图

```
DashboardOverview
├─ kpi: KPIData
├─ trends: List[TrendPoint]
├─ inventory_alerts: List[InventoryAlert]
└─ finance_status: FinanceStatus
```

---

## 🚀 模块 3: Dashboard API 接口

### 文件路径
```
backend/app/api/v1/endpoints/dashboard.py
```

### 3.1 主接口: GET /overview

#### 接口定义

```python
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
```

#### 数据查询流程

```
┌─────────────────────────────────────┐
│ 1. 查询 KPI 数据 (本月)            │
│    ├─ 销售总额                     │
│    ├─ 毛利总额                     │
│    ├─ 订单数                       │
│    └─ 计算毛利率                   │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│ 2. 查询销售趋势 (过去30天)         │
│    ├─ 按日期分组                   │
│    ├─ 聚合销售额                   │
│    └─ 聚合毛利                     │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│ 3. 查询库存预警 (TOP 5)            │
│    ├─ 筛选: 缺货/库存不足          │
│    ├─ 排序: 缺货优先，库存量升序   │
│    └─ 限制: 前5条                  │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│ 4. 查询资金状况                    │
│    ├─ 应收账款总额                 │
│    ├─ 应付账款总额                 │
│    └─ 本月费用总额                 │
└─────────────────────────────────────┘
```

#### 核心 SQL 语句

**1. KPI 查询 SQL**

```sql
SELECT 
    COALESCE(SUM(sales_amount), 0) as total_sales,
    COALESCE(SUM(gross_profit), 0) as gross_profit,
    COUNT(DISTINCT order_id) as order_count
FROM view_bi_sales_analysis
WHERE EXTRACT(YEAR FROM order_date) = EXTRACT(YEAR FROM CURRENT_DATE)
    AND EXTRACT(MONTH FROM order_date) = EXTRACT(MONTH FROM CURRENT_DATE)
    AND order_status IN ('confirmed', 'completed')
```

**关键点**:
- `COALESCE`: 处理空值，默认返回 0
- `DISTINCT order_id`: 避免订单明细重复计数
- `order_status`: 仅统计已确认和已完成订单

**2. 销售趋势 SQL**

```sql
SELECT 
    TO_CHAR(order_date, 'YYYY-MM-DD') as date_str,
    COALESCE(SUM(sales_amount), 0) as sales,
    COALESCE(SUM(gross_profit), 0) as profit
FROM view_bi_sales_analysis
WHERE order_date >= CURRENT_DATE - INTERVAL '30 days'
    AND order_status IN ('confirmed', 'completed')
GROUP BY order_date
ORDER BY order_date ASC
```

**关键点**:
- `TO_CHAR`: 格式化日期为字符串 (前端展示)
- `INTERVAL '30 days'`: 过去 30 天
- `GROUP BY order_date`: 按天聚合

**3. 库存预警 SQL**

```sql
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
```

**关键点**:
- `CASE`: 自定义排序优先级 (缺货 > 库存不足)
- `current_stock ASC`: 同状态下按库存量升序
- `LIMIT 5`: 仅返回前 5 条预警

**4. 资金状况 SQL (3个查询)**

```sql
-- 应收账款
SELECT COALESCE(SUM(current_balance), 0) as total_receivable
FROM view_bi_finance_monitor
WHERE record_type = 'receivable' AND current_balance > 0

-- 应付账款
SELECT COALESCE(SUM(current_balance), 0) as total_payable
FROM view_bi_finance_monitor
WHERE record_type = 'payable' AND current_balance > 0

-- 本月费用
SELECT COALESCE(SUM(trans_amount), 0) as total_expense
FROM view_bi_finance_monitor
WHERE record_type = 'expense'
    AND EXTRACT(YEAR FROM trans_date) = EXTRACT(YEAR FROM CURRENT_DATE)
    AND EXTRACT(MONTH FROM trans_date) = EXTRACT(MONTH FROM CURRENT_DATE)
```

#### 数据类型转换

```python
def decimal_to_float(value: Any) -> float:
    """将 Decimal 转换为 float"""
    if isinstance(value, Decimal):
        return float(value)
    return value
```

**为什么需要转换?**
- PostgreSQL 的 `NUMERIC` 类型在 Python 中映射为 `Decimal`
- JSON 不直接支持 `Decimal` 类型
- 前端 JavaScript 使用 `Number` (相当于 float)

### 3.2 辅助接口: GET /kpi

#### 接口定义

```python
@router.get("/kpi")
async def get_kpi(db: AsyncSession = Depends(get_db)):
    """单独获取 KPI 数据"""
```

**使用场景**: 前端需要单独刷新 KPI 卡片时调用

---

## 🤖 模块 4: Vanna AI 服务

### 文件路径
```
backend/app/services/vanna_service.py
```

### 4.1 AI 模型训练

#### 训练方法实现

```python
async def _train_ai_models(self):
    """
    训练 Vanna AI 模型
    
    为 AI 提供数据库结构知识：
    1. 训练销售分析视图 (view_bi_sales_analysis)
    2. 训练财务监控视图 (view_bi_finance_monitor)
    3. 训练库存预警视图 (view_bi_inventory_alert)
    4. 训练采购分析视图 (view_bi_purchase_analysis)
    """
    print("🤖 开始训练 Vanna AI 模型...")
    
    # TODO: 实际集成 Vanna.ai 时，取消下面的注释
    # await vanna.train(ddl="CREATE VIEW ...", documentation="...")
    
    print("✅ Vanna AI 模型训练完成 (当前为模拟模式)")
```

#### 训练数据结构

**销售分析视图训练数据**:
```python
await vanna.train(
    ddl="""
    CREATE VIEW view_bi_sales_analysis AS ...
    字段说明:
    - company_name: 分公司名称
    - salesman_name: 业务员姓名
    - partner_name: 客户名称
    - region: 客户地区 (华东/华北/华南等)
    - product_name: 商品名称
    - category: 商品分类
    - sales_amount: 销售额
    - gross_profit: 毛利
    - gross_profit_rate: 毛利率
    """
)
```

### 4.2 模拟 SQL 生成

#### 实现逻辑

```python
def _mock_generate_sql(self, question: str, context: Dict[str, Any] = None) -> str:
    """模拟 SQL 生成 (临时实现)"""
    question_lower = question.lower()

    if "销售" in question_lower or "销售额" in question_lower:
        return """
        SELECT
            DATE_TRUNC('month', order_date) as month,
            SUM(sales_amount) as total_sales,
            SUM(gross_profit) as total_profit,
            COUNT(DISTINCT order_id) as order_count
        FROM view_bi_sales_analysis
        WHERE order_date >= CURRENT_DATE - INTERVAL '12 months'
        GROUP BY DATE_TRUNC('month', order_date)
        ORDER BY month DESC
        """
    # ... 更多场景
```

#### 问题映射表

| 用户问题关键词 | 查询视图 | 聚合维度 | 时间范围 |
|---------------|---------|---------|---------|
| 销售、销售额 | `view_bi_sales_analysis` | 月度 | 近12个月 |
| 库存、预警 | `view_bi_inventory_alert` | 商品+仓库 | 当前 |
| 费用、应收、应付 | `view_bi_finance_monitor` | 部门+科目 | 近3个月 |

### 4.3 宽表视图说明

#### 为什么使用宽表视图?

```
传统方式 (多表 JOIN):
┌─────────┐     ┌─────────┐     ┌─────────┐
│ 订单表  │ ─── │ 商品表  │ ─── │ 客户表  │
└─────────┘     └─────────┘     └─────────┘
      │               │               │
      └───────────────┴───────────────┘
                      │
            AI 需要理解复杂 JOIN 逻辑
                  (困难!)

宽表视图方式:
┌─────────────────────────────────────────┐
│   view_bi_sales_analysis (扁平化)       │
│  ├─ 订单信息                            │
│  ├─ 商品信息 (已 JOIN)                  │
│  ├─ 客户信息 (已 JOIN)                  │
│  ├─ 业务员信息 (已 JOIN)                │
│  └─ 预计算指标 (毛利、毛利率)           │
└─────────────────────────────────────────┘
                │
        AI 直接查询扁平数据
            (简单!)
```

#### 视图字段设计原则

1. **维度字段**: 所有可能的分组维度都铺平
   - 分公司、部门、业务员
   - 客户、地区
   - 商品、分类
   - 仓库

2. **度量字段**: 核心指标预计算
   - 销售额、成本、毛利
   - 毛利率
   - 库存数量、库存价值

3. **时间字段**: 拆分到多个粒度
   - `order_date`: 原始日期
   - `year`: 年份
   - `month`: 月份

---

## 🔗 模块 5: 路由注册

### 文件路径
```
backend/app/main.py
```

### 路由注册代码

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import chat, report, dashboard
from app.core.config import settings

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
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(report.router, prefix="/api/v1/report", tags=["report"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])
```

### API 路由结构

```
/api/v1
├─ /chat
│  ├─ POST /              ← AI 智能问答
│  └─ GET /history        ← 聊天历史
├─ /report
│  ├─ POST /query         ← 报表查询
│  └─ POST /export        ← 报表导出
└─ /dashboard
   ├─ GET /overview       ← Dashboard 总览 ⭐
   └─ GET /kpi            ← KPI 指标
```

### FastAPI 自动文档

启动服务后访问:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## 📝 Schema 导出配置

### 文件路径
```
backend/app/schemas/__init__.py
```

### 导出配置

```python
"""
Pydantic 模型定义
"""
from .chat import *
from .report import *
from .dashboard import *

__all__ = [
    "ChatRequest", 
    "ChatResponse", 
    "ReportRequest", 
    "ExportRequest",
    "DashboardOverview",
    "KPIData",
    "TrendPoint",
    "InventoryAlert",
    "FinanceStatus"
]
```

**作用**: 统一导出接口，方便其他模块引用

---

## 🧪 测试与验证

### 启动后端服务

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 测试接口

#### 1. 测试 Dashboard 总览

```bash
curl http://localhost:8000/api/v1/dashboard/overview
```

**预期响应**:
```json
{
  "kpi": {
    "total_sales": "125000.00",
    "gross_profit": "35000.00",
    "order_count": 150,
    "gross_profit_rate": 28.0
  },
  "trends": [
    {
      "date": "2026-01-01",
      "sales": 5000.0,
      "profit": 1400.0
    }
  ],
  "inventory_alerts": [
    {
      "product_name": "笔记本电脑",
      "current_stock": 5.0,
      "min_stock": 10.0,
      "warehouse_name": "北京总仓",
      "stock_status": "库存不足"
    }
  ],
  "finance_status": {
    "total_receivable": "80000.00",
    "total_payable": "50000.00",
    "total_expense": "20000.00"
  }
}
```

#### 2. 测试 KPI 接口

```bash
curl http://localhost:8000/api/v1/dashboard/kpi
```

#### 3. 测试 AI 问答

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "本月的销售额是多少？"}'
```

### 使用 FastAPI 自动文档测试

1. 打开浏览器访问 `http://localhost:8000/docs`
2. 找到 `dashboard` 标签下的接口
3. 点击 `Try it out` 按钮
4. 点击 `Execute` 执行测试

---

## 🔍 关键技术细节

### 1. 异步数据库查询

**为什么使用异步?**
- Dashboard 需要并发查询多个数据源 (KPI、趋势、库存、财务)
- 异步可以避免阻塞，提升响应速度

**性能对比**:
```
同步查询 (串行):
Query 1: 100ms ─┐
                ├─> Query 2: 150ms ─┐
                                    ├─> Query 3: 120ms ─┐
                                                        ├─> Query 4: 80ms
总耗时: 450ms

异步查询 (并行):
Query 1: 100ms ─┐
Query 2: 150ms ─┤
Query 3: 120ms ─┼─> 等待最慢的完成
Query 4: 80ms  ─┘
总耗时: 150ms (最慢查询的时间)
```

**未来优化**: 可以使用 `asyncio.gather()` 并行执行 4 个查询

```python
# 优化方案示例
kpi_task = db.execute(kpi_sql)
trend_task = db.execute(trend_sql)
inventory_task = db.execute(inventory_sql)
finance_task = db.execute(finance_sql)

results = await asyncio.gather(
    kpi_task, trend_task, inventory_task, finance_task
)
```

### 2. Decimal vs Float 处理

**问题**: PostgreSQL `NUMERIC` → Python `Decimal` → JSON ❌

**解决方案**:
```python
# 方案1: 手动转换 (当前方案)
sales = decimal_to_float(row[0])

# 方案2: Pydantic 配置 (推荐)
class KPIData(BaseModel):
    total_sales: Decimal
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }
```

### 3. SQL 注入防护

**使用 `text()` 时的安全实践**:

```python
# ❌ 危险: 直接拼接
sql = f"SELECT * FROM users WHERE name = '{user_input}'"

# ✅ 安全: 使用参数化查询
sql = text("SELECT * FROM users WHERE name = :name")
result = await db.execute(sql, {"name": user_input})
```

**当前实现**: 所有 SQL 都是硬编码，无用户输入，安全 ✅

---

## 📈 性能优化建议

### 1. 数据库索引

```sql
-- 订单表索引
CREATE INDEX idx_biz_order_date_status 
ON biz_order(order_date, status);

CREATE INDEX idx_biz_order_salesman 
ON biz_order(salesman_id);

-- 财务表索引
CREATE INDEX idx_fact_finance_date_type 
ON fact_finance(trans_date, record_type);

-- 库存表索引
CREATE INDEX idx_inv_stock_product_warehouse 
ON inv_current_stock(product_id, warehouse_id);
```

### 2. Redis 缓存

```python
# 缓存 Dashboard 数据 (5分钟)
cache_key = "dashboard:overview"
cached = await redis.get(cache_key)

if cached:
    return json.loads(cached)

# 查询数据库
data = await query_dashboard_data()

# 缓存结果
await redis.setex(cache_key, 300, json.dumps(data))
```

### 3. 数据库连接池

```python
engine = create_async_engine(
    settings.database_url,
    pool_size=10,          # 连接池大小
    max_overflow=20,       # 最大溢出连接
    pool_pre_ping=True,    # 连接前检查
    pool_recycle=3600,     # 连接回收时间(秒)
)
```

---

## 🐛 常见问题排查

### 问题 1: 接口返回空数据

**原因**: 数据库中无数据或视图未创建

**解决**:
```bash
# 1. 检查视图是否存在
psql -U postgres -d inventory_bi -c "\dv"

# 2. 重新创建视图
psql -U postgres -d inventory_bi -f backend/app/db/init_views.sql

# 3. 插入测试数据
python backend/scripts/init_db.py
```

### 问题 2: Decimal 序列化失败

**错误**: `Object of type Decimal is not JSON serializable`

**解决**: 使用 `decimal_to_float()` 转换或配置 Pydantic `json_encoders`

### 问题 3: 数据库连接失败

**错误**: `could not connect to server`

**检查清单**:
- [ ] PostgreSQL 服务是否启动
- [ ] 数据库连接字符串是否正确
- [ ] 防火墙是否允许 5432 端口
- [ ] 数据库用户权限是否足够

```bash
# 测试连接
psql -U postgres -h localhost -p 5432 -d inventory_bi
```

---

## 📚 相关文档

- [PRD 产品需求文档](./2_prd.md)
- [技术栈说明](./3_tech_stack.md)
- [BI 交互标准](./5_bi_interaction_standards.md)
- [数据库模型文档](../backend/app/db/README.md)

---

## 🎯 后续优化计划

### 短期优化 (1-2周)

- [ ] 实现 Redis 缓存
- [ ] 添加单元测试
- [ ] 优化 SQL 查询 (使用 `asyncio.gather` 并行查询)
- [ ] 添加接口限流

### 中期优化 (1个月)

- [ ] 集成真实 Vanna.ai API
- [ ] 实现 AI 模型训练逻辑
- [ ] 添加查询日志和监控
- [ ] 实现数据权限控制 (行级安全)

### 长期优化 (3个月)

- [ ] 实现实时数据推送 (WebSocket)
- [ ] 添加数据导出功能 (Excel/CSV)
- [ ] 实现自定义 Dashboard 配置
- [ ] 添加数据可视化推荐算法

---

## 📞 技术支持

如有问题或建议，请联系开发团队。

**文档维护**: 开发团队  
**最后更新**: 2026-01-05  
**文档版本**: v1.0.0
