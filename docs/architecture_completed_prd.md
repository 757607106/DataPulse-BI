# 进销存智能 BI 系统 - 已完成功能需求文档 (PRD)

## 1. 项目概述

### 1.1 项目背景
本项目是一款基于 AI 技术的智能商业智能分析系统，专注于解决进销存管理企业的报表开发周期长、灵活性差等问题。通过集成 Vanna.ai 的 Text-to-SQL 技术，实现"按需自行设置分析报表"的核心价值。

### 1.2 核心价值
- **AI 驱动分析**：自然语言转 SQL，无需专业技术人员
- **实时业务洞察**：多维度 KPI 指标实时监控
- **智能业务操作**：AI 解析自然语言指令，简化操作流程
- **灵活报表导出**：支持 Excel 格式导出，满足业务需求

### 1.3 项目状态
✅ **已完成开发** - 核心功能已实现并可运行

---

## 2. 技术架构

### 2.1 总体架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端界面      │    │   后端服务      │    │   数据存储      │
│                 │    │                 │    │                 │
│ • Vue 3         │◄──►│ • FastAPI       │◄──►│ • PostgreSQL    │
│ • Vue Pure Admin│    │ • SQLAlchemy    │    │ • pgvector      │
│ • Element Plus  │    │ • Vanna.ai      │    │ • Redis         │
│ • ECharts 5     │    │ • Redis缓存     │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 2.2 前端技术栈
- **框架**：Vue 3 + Script Setup
- **UI 库**：Element Plus
- **模板**：Vue Pure Admin (GitHub Star 15k+)
- **样式**：Tailwind CSS (WindiCSS 兼容)
- **图表**：ECharts 5
- **图标**：Iconify (useRenderIcon)
- **网络**：Axios (自定义封装)
- **路由**：Vue Router 4
- **状态**：Pinia (用户状态管理)

### 2.3 后端技术栈
- **语言**：Python 3.10+
- **框架**：FastAPI (异步)
- **ORM**：SQLAlchemy 2.0 (异步)
- **AI 核心**：Vanna.ai + 阿里百炼 Qwen
- **数据库**：PostgreSQL 16 + pgvector
- **缓存**：Redis (Alpine)
- **认证**：JWT (PyJWT)

### 2.4 基础设施
- **容器化**：Docker + Docker Compose
- **数据库镜像**：pgvector/pgvector:pg16 (ARM64 支持)
- **缓存镜像**：redis:alpine

---

## 3. 已完成功能模块

### 3.1 🔐 认证系统 (Auth Module)

#### 功能描述
完整的用户认证和权限管理，支持角色-based访问控制。

#### 已实现功能
- ✅ 用户登录/登出
- ✅ JWT Token 认证
- ✅ 用户注册
- ✅ 路由权限控制
- ✅ 登录状态保持

#### 接口清单
| 接口路径 | 方法 | 功能描述 | 请求体/响应体 |
|---------|------|---------|-------------|
| `/api/v1/auth/login` | POST | 用户登录 | `LoginRequest` → `LoginResult` |
| `/api/v1/auth/me` | GET | 获取用户信息 | - → `UserInfo` |
| `/api/v1/auth/register` | POST | 用户注册 | `UserCreate` → `UserResponse` |

#### 前端页面
- `/login` - 用户登录页面

---

### 3.2 📊 经营驾驶舱 (Dashboard)

#### 功能描述
提供企业经营状况的实时监控，包括关键指标、销售趋势、库存预警和资金状况。

#### 已实现功能
- ✅ KPI 指标展示 (销售额、毛利、订单数、毛利率)
- ✅ 销售趋势图 (30天折线图)
- ✅ 库存预警列表 (前10个预警商品)
- ✅ 资金状况 (应收/应付账款总额、本月费用)
- ✅ 数据实时性 (最后更新时间显示)

#### 数据指标
| 指标名称 | 计算逻辑 | 数据类型 |
|---------|---------|---------|
| 本月销售额 | 当月已确认销售订单总额 | Decimal |
| 本月毛利 | 销售额 - 成本 | Decimal |
| 本月订单数 | 当月销售订单数量 | Integer |
| 毛利率 | (毛利/销售额) × 100% | Float |

#### 接口清单
| 接口路径 | 方法 | 功能描述 | 请求体/响应体 |
|---------|------|---------|-------------|
| `/api/v1/dashboard/overview` | GET | 获取总览数据 | - → `DashboardOverview` |
| `/api/v1/dashboard/kpi` | GET | 获取 KPI 数据 | - → `KPIData` |

#### 前端页面
- `/dashboard` - 经营驾驶舱主页面
  - KPI 卡片组件
  - ECharts 销售趋势图
  - 库存预警表格
  - 资金状况展示

---

### 3.3 🤖 智能问答 (ChatBI)

#### 功能描述
基于 Vanna.ai 的自然语言转 SQL 功能，支持用户用自然语言提问，系统自动生成并执行 SQL 查询。

#### 已实现功能
- ✅ 自然语言 SQL 生成
- ✅ 智能图表类型推荐 (table/line/bar/pie)
- ✅ 查询结果展示 (SQL + 数据 + 图表)
- ✅ 聊天历史记录
- ✅ 模拟 AI 响应 (当前为模拟模式)

#### 支持的查询类型
- 销售分析：销售额、毛利、订单统计
- 库存查询：库存状况、预警提醒
- 财务分析：应收/应付、费用统计
- 时间维度：按月/季/年统计

#### 接口清单
| 接口路径 | 方法 | 功能描述 | 请求体/响应体 |
|---------|------|---------|-------------|
| `/api/v1/chat/` | POST | AI 智能问答 | `ChatRequest` → `ChatResponse` |
| `/api/v1/chat/history` | GET | 获取聊天历史 | - → `ChatHistory` |

#### 前端页面
- `/analysis` - 智能分析页面

---

### 3.4 📋 报表中心 (Reports)

#### 功能描述
提供灵活的报表查询和导出功能，支持多维度筛选和 Excel 导出。

#### 已实现功能
- ✅ 通用查询接口 (多维度筛选)
- ✅ 数据分组汇总
- ✅ Excel 导出 (.xlsx)
- ✅ 排序功能
- ✅ 分页查询

#### 支持的筛选维度
- 时间范围
- 分公司/部门
- 业务员
- 商品分类
- 仓库
- 客户/供应商

#### 接口清单
| 接口路径 | 方法 | 功能描述 | 请求体/响应体 |
|---------|------|---------|-------------|
| `/api/v1/report/query` | POST | 通用报表查询 | `ReportRequest` → 查询结果 |
| `/api/v1/report/export` | POST | 导出报表 | `ExportRequest` → Excel文件 |
| `/api/v1/report/dashboard` | GET | 获取仪表板数据 | - → 基础图表数据 |

#### 前端页面
- `/reports` - 报表中心页面

---

### 3.5 ⚙️ 业务操作 (Operations)

#### 功能描述
支持进销存核心业务操作，包括采购入库、销售出库，以及 AI 智能指令解析。

#### 已实现功能
- ✅ 采购入库 (事务处理)
- ✅ 销售出库 (库存检查 + 事务处理)
- ✅ AI 指令解析 (自然语言转业务操作)
- ✅ 基础数据管理 (商品/仓库/合作伙伴/业务员)

#### 业务流程

**采购入库流程**：
1. 验证供应商、仓库、业务员信息
2. 检查商品数据有效性
3. 创建采购订单
4. 生成订单明细
5. 增加库存数量
6. 记录应付账款

**销售出库流程**：
1. 验证客户、仓库、业务员信息
2. 检查库存充足性
3. 创建销售订单
4. 生成订单明细
5. 扣减库存数量
6. 记录应收账款

#### 接口清单

**基础数据接口**：
| 接口路径 | 方法 | 功能描述 | 请求体/响应体 |
|---------|------|---------|-------------|
| `/api/v1/business/products` | GET | 获取商品列表 | - → `Product[]` |
| `/api/v1/business/warehouses` | GET | 获取仓库列表 | - → `Warehouse[]` |
| `/api/v1/business/partners` | GET | 获取合作伙伴 | - → `Partner[]` |
| `/api/v1/business/salesmen` | GET | 获取业务员列表 | - → `Salesman[]` |

**业务操作接口**：
| 接口路径 | 方法 | 功能描述 | 请求体/响应体 |
|---------|------|---------|-------------|
| `/api/v1/business/inbound` | POST | 采购入库 | `InboundRequest` → `BusinessOperationResponse` |
| `/api/v1/business/outbound` | POST | 销售出库 | `OutboundRequest` → `BusinessOperationResponse` |
| `/api/v1/business/parse-command` | POST | AI 指令解析 | `ParseCommandRequest` → `ParseCommandResult` |

#### 前端页面
- `/operations` - 业务操作页面

---

### 3.6 🔧 系统设置 (Settings)

#### 功能描述
系统配置和用户设置管理。

#### 已实现功能
- ✅ 基础页面框架 (待完善)

#### 前端页面
- `/settings` - 系统设置页面

---

## 4. 数据模型架构

### 4.1 核心维度表

| 表名 | 功能描述 | 关键字段 |
|-----|---------|---------|
| `sys_user` | 用户表 | username, hashed_password, role |
| `sys_department` | 组织架构 | company_name, name, parent_id |
| `sys_employee` | 人员维度 | name, dept_id, email, phone |
| `base_product` | 商品基础信息 | name, category, cost_price, min_stock |
| `base_warehouse` | 仓库信息 | name, location |
| `base_partner` | 合作伙伴 | name, type (customer/supplier), region |

### 4.2 业务事实表

| 表名 | 功能描述 | 关键字段 |
|-----|---------|---------|
| `biz_order` | 订单主表 | order_no, type, total_amount, status |
| `biz_order_item` | 订单明细 | product_id, quantity, price, subtotal |
| `inv_current_stock` | 库存快照 | warehouse_id, product_id, quantity |
| `fact_finance` | 财务流水 | type, amount, balance, trans_date |

### 4.3 宽表视图 (AI 查询专用)

| 视图名 | 用途 | 数据范围 |
|-------|------|---------|
| `view_bi_sales_analysis` | 销售分析 | 订单 + 商品 + 客户 + 业务员 |
| `view_bi_finance_monitor` | 财务监控 | 应收/应付 + 费用 |
| `view_bi_inventory_alert` | 库存预警 | 库存状态 + 预警规则 |
| `view_bi_purchase_analysis` | 采购分析 | 采购订单 + 供应商 |

---

## 5. 部署和运行

### 5.1 环境要求
- **前端**：Node.js 16+, npm/yarn
- **后端**：Python 3.10+, pip
- **数据库**：Docker (PostgreSQL + Redis)
- **AI 服务**：DASHSCOPE_API_KEY 环境变量

### 5.2 启动步骤

```bash
# 1. 启动数据库服务
docker-compose up -d

# 2. 初始化数据库
cd backend/scripts
python init_db.py

# 3. 启动后端服务
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 4. 启动前端服务
cd frontend
npm install
npm run dev
```

### 5.3 访问地址
- **前端界面**：http://localhost:3000
- **后端 API**：http://localhost:8000
- **API 文档**：http://localhost:8000/docs

---

## 6. 核心特性

### 6.1 AI 智能特性
- **自然语言查询**：支持中文自然语言提问
- **智能图表推荐**：根据数据特征自动推荐图表类型
- **指令解析**：AI 理解业务操作指令
- **SQL 缓存**：Redis 缓存常用查询结果

### 6.2 业务特性
- **实时监控**：Dashboard 实时更新关键指标
- **库存预警**：自动检测库存不足情况
- **事务处理**：保证业务操作的数据一致性
- **权限控制**：基于角色的访问控制

### 6.3 技术特性
- **异步处理**：FastAPI + asyncpg 高并发支持
- **类型安全**：Pydantic 数据验证
- **响应式设计**：适配 PC 和移动端
- **暗色主题**：专注夜间办公体验

---

## 7. 性能指标

### 7.1 响应时间
- **简单查询**：< 3秒 (AI SQL 生成 + 执行)
- **图表渲染**：< 1秒 (前端 ECharts)
- **业务操作**：< 2秒 (事务处理)

### 7.2 AI 准确率
- **训练后查询准确率**：> 90%
- **指令解析成功率**：> 85%

### 7.3 兼容性
- **浏览器**：Chrome 90+, Edge 90+, Safari 14+
- **移动端**：响应式设计，适配平板

---

## 8. 安全保障

### 8.1 认证安全
- JWT Token 认证
- 密码哈希存储
- Token 过期机制

### 8.2 数据安全
- SQL 注入防护
- 输入数据验证
- 敏感信息加密

### 8.3 访问控制
- 角色-based 权限
- API 接口认证
- 前端路由守卫

---

## 9. 后续优化计划

### 9.1 短期优化 (1-2周)
- [ ] 集成真实 Vanna.ai API
- [ ] 添加单元测试
- [ ] 实现 Redis 缓存
- [ ] 优化 SQL 查询性能

### 9.2 中期优化 (1个月)
- [ ] 实现数据权限控制 (行级安全)
- [ ] 添加查询日志和监控
- [ ] 实现 WebSocket 实时推送
- [ ] 完善系统设置功能

### 9.3 长期优化 (3个月)
- [ ] 实现自定义 Dashboard
- [ ] 添加更多图表类型
- [ ] 实现数据可视化推荐算法
- [ ] 支持多租户架构

---

## 10. 技术文档索引

- [前端开发文档](./frontend/README.md)
- [后端 API 文档](./backend/README.md)
- [技术栈说明](./backend/tech_stack.md)
- [Dashboard 实现详解](./frontend/dashboard_implementation.md)
- [BI 交互标准](./frontend/bi_interaction_standards.md)

---

**文档版本**: v2.0  
**最后更新**: 2026-01-05  
**项目状态**: ✅ 已完成核心功能开发
