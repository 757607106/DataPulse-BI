# 进销存智能 BI 系统

基于 Vue 3 + FastAPI + AI (Vanna) 的全栈商业智能分析系统，实现自然语言查询、AI 驱动的智能报表和可视化分析。

## 📋 项目概述

这是一个现代化的进销存 BI 系统，集成了人工智能技术，能够通过自然语言理解用户需求，自动生成 SQL 查询，并提供丰富的可视化图表展示。

### ✨ 核心特性

- **🧠 AI 智能问答**: 自然语言转 SQL，零门槛数据查询
- **📊 经营驾驶舱**: 实时 KPI 监控和业务指标展示
- **📈 智能图表**: 自动推荐最适合的图表类型
- **🔍 通用查询**: 多维度组合筛选和数据钻取
- **📤 数据导出**: 支持 Excel/CSV 格式导出
- **🔐 权限控制**: 基于角色的访问控制(RBAC)

## 🏗️ 项目架构

### 技术栈

**前端 (Vue 3)**
- Vue 3 + TypeScript + Vite
- Element Plus + ECharts 5
- Tailwind CSS + Pinia
- Axios (HTTP 客户端)

**后端 (FastAPI)**
- Python 3.10+ + FastAPI
- PostgreSQL + pgvector
- Redis (缓存)
- Vanna.ai + 阿里百炼

**基础设施**
- Docker & Docker Compose
- pgvector (向量数据库)
- Redis (缓存层)

### 目录结构

```
DataPulse BI/
├── docker-compose.yml           # Docker 编排配置
├── backend/                     # 后端服务
│   ├── app/
│   │   ├── main.py             # FastAPI 应用入口
│   │   ├── api/v1/endpoints/   # API 端点
│   │   │   ├── auth.py         # 用户认证接口
│   │   │   ├── business.py     # 业务操作接口
│   │   │   ├── chat.py         # ChatBI 智能问答接口
│   │   │   ├── dashboard.py    # 仪表板数据接口
│   │   │   └── report.py       # 报表查询接口
│   │   ├── core/               # 核心配置
│   │   │   ├── config.py       # 应用配置
│   │   │   └── security.py     # 安全配置
│   │   ├── db/                 # 数据库相关
│   │   │   ├── session.py      # 数据库会话管理
│   │   │   ├── init_db.py      # 数据库初始化
│   │   │   ├── init_views.sql  # 视图初始化SQL
│   │   │   └── README.md       # 数据库文档
│   │   ├── models/             # SQLAlchemy 模型
│   │   │   ├── base.py         # 基础模型定义
│   │   │   └── bi_schema.py    # BI 数据模型
│   │   ├── schemas/            # Pydantic 数据验证模型
│   │   │   ├── auth.py         # 认证相关模型
│   │   │   ├── business.py     # 业务相关模型
│   │   │   ├── chat.py         # 聊天相关模型
│   │   │   ├── dashboard.py    # 仪表板相关模型
│   │   │   └── report.py       # 报表相关模型
│   │   └── services/           # 业务服务层
│   │       └── vanna_service.py # Vanna AI 服务
│   ├── requirements.txt        # Python 依赖
│   ├── scripts/                # 脚本工具
│   │   └── init_db.py          # 数据库初始化脚本
│   └── test_*.py               # 测试文件
├── frontend/                    # 前端应用
│   ├── src/
│   │   ├── api/                 # API 接口封装
│   │   │   ├── auth.ts          # 认证接口
│   │   │   ├── business.ts      # 业务接口
│   │   │   └── dashboard.ts     # 仪表板接口
│   │   ├── components/          # 组件
│   │   │   ├── Charts/          # ECharts 图表组件
│   │   │   │   ├── BaseChart.vue # 基础图表组件
│   │   │   │   ├── Example.vue   # 示例组件
│   │   │   │   └── index.ts      # 组件导出
│   │   │   └── Layout/          # 布局组件
│   │   │       └── AppLayout.vue # 主应用布局
│   │   ├── router/              # 路由配置
│   │   │   └── index.ts         # 路由定义
│   │   ├── stores/              # Pinia 状态管理
│   │   │   └── user.ts          # 用户状态管理
│   │   ├── types/               # TypeScript 类型定义
│   │   │   ├── dashboard.ts     # 仪表板类型
│   │   │   └── echarts.ts       # ECharts 类型
│   │   ├── utils/               # 工具函数
│   │   │   └── http.ts          # HTTP 请求封装
│   │   └── views/               # 页面视图
│   │       ├── Login/           # 登录页面
│   │       ├── Dashboard/       # 经营驾驶舱
│   │       ├── Analysis/        # 智能分析页面
│   │       ├── Reports/         # 报表中心
│   │       ├── Operations/      # 业务操作
│   │       └── Settings/        # 系统设置
│   ├── DASHBOARD_API_GUIDE.md   # 仪表板 API 指南
│   ├── package.json             # 前端依赖配置
│   ├── vite.config.ts           # Vite 配置
│   ├── tsconfig.json            # TypeScript 配置
│   └── tailwind.config.js       # Tailwind CSS 配置
├── docs/                        # 项目文档
│   ├── prd.md                   # 产品需求文档
│   ├── backend/                 # 后端文档
│   │   └── tech_stack.md        # 技术栈说明
│   └── frontend/                # 前端文档
│       ├── bi_interaction_standards.md  # BI 交互规范
│       └── dashboard_implementation.md  # 仪表板实现指南
├── figma_source/                # Figma 设计源代码
├── init-db.sql/                 # 数据库初始化SQL目录
├── start_backend.sh             # 后端启动脚本
├── start_frontend.sh            # 前端启动脚本
├── STARTUP_GUIDE.md             # 启动指南
└── README.md                    # 项目说明文档
```

## 🚀 快速开始

### 环境要求

- Docker & Docker Compose
- Python 3.10+
- Node.js 16+
- Git

### 1. 克隆项目

```bash
git clone <repository-url>
cd inventory-bi-system
```

### 2. 配置环境变量

创建 `.env` 文件在项目根目录：

```bash
# AI 服务配置
DASHSCOPE_API_KEY=your-dashscope-api-key

# 数据库配置 (可选，默认使用 Docker)
DATABASE_URL=postgresql+asyncpg://postgres:postgres123@localhost:5432/inventory_bi
REDIS_URL=redis://localhost:6379/0
```

### 3. 启动 Docker 环境

```bash
# 启动所有服务 (PostgreSQL + Redis + 后端 + 前端)
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 4. 访问应用

- **前端界面**: http://localhost:3000
- **后端 API 文档**: http://localhost:8000/docs
- **数据库**: localhost:5432
- **Redis**: localhost:6379

### 5. 初始化数据 (可选)

如果需要初始化测试数据，可以执行：

```bash
# 进入后端容器
docker-compose exec backend bash

# 运行数据初始化脚本 (需要先创建)
python init_data.py
```

## 📁 目录详细说明

### 根目录文件

- **`docker-compose.yml`**: Docker 容器编排配置，包含 PostgreSQL、Redis、后端、前端四个服务
- **`init-db.sql/`**: 数据库初始化 SQL 脚本目录
- **`start_backend.sh`**: 后端服务快速启动脚本
- **`start_frontend.sh`**: 前端服务快速启动脚本
- **`STARTUP_GUIDE.md`**: 项目启动和部署指南
- **`README.md`**: 项目说明文档

### docs/ 文档目录

- **`prd.md`**: 产品需求文档，详细描述功能模块和业务逻辑
- **`backend/tech_stack.md`**: 后端技术栈架构说明
- **`frontend/bi_interaction_standards.md`**: BI 系统交互规范，参考主流 BI 产品设计
- **`frontend/dashboard_implementation.md`**: 仪表板实现指南和最佳实践

### backend/ 后端目录

#### app/main.py
FastAPI 应用入口文件，配置路由、中间件和应用基本信息。

#### app/api/v1/endpoints/
- **`auth.py`**: 用户认证接口，包含登录、注册、权限验证
- **`business.py`**: 业务操作接口，处理业务数据的增删改查
- **`chat.py`**: ChatBI 智能问答接口，实现自然语言转 SQL 功能
- **`dashboard.py`**: 仪表板数据接口，提供 KPI 和图表数据
- **`report.py`**: 报表查询和导出接口，支持通用查询和数据导出

#### app/core/
- **`config.py`**: 应用配置文件，管理数据库、Redis、AI 服务等配置
- **`security.py`**: 安全配置模块，包含 JWT 认证、密码哈希、权限检查

#### app/services/
- **`vanna_service.py`**: Vanna AI 服务核心模块，负责 SQL 生成、查询执行、图表推荐等

#### app/models/
- **`base.py`**: SQLAlchemy 基础模型定义

#### app/db/
数据库相关模块：
- **`session.py`**: 数据库会话管理和连接池配置
- **`init_db.py`**: 数据库初始化和表创建脚本
- **`init_views.sql`**: 数据视图初始化 SQL 脚本
- **`README.md`**: 数据库设计和使用说明文档

#### app/models/
SQLAlchemy 数据模型：
- **`base.py`**: 基础模型类和数据库配置
- **`bi_schema.py`**: BI 业务相关的数据库表和视图定义

#### app/schemas/
Pydantic 数据验证模型：
- **`auth.py`**: 用户认证相关的请求/响应模型
- **`business.py`**: 业务操作相关的请求/响应模型
- **`chat.py`**: 聊天和 AI 问答相关的请求/响应模型
- **`dashboard.py`**: 仪表板数据相关的请求/响应模型
- **`report.py`**: 报表查询相关的请求/响应模型

### frontend/ 前端目录

#### src/api/
API 接口封装层，对后端接口进行统一封装和管理：
- **`auth.ts`**: 用户认证相关接口封装
- **`business.ts`**: 业务操作相关接口封装
- **`dashboard.ts`**: 仪表板数据相关接口封装

#### src/components/
组件库和布局组件：
- **`Charts/`**: ECharts 图表组件封装
  - **`BaseChart.vue`**: 基础图表组件
  - **`Example.vue`**: 图表示例组件
- **`Layout/AppLayout.vue`**: 主应用布局组件，包含侧边栏和导航

#### src/router/
路由配置：
- **`index.ts`**: Vue Router 配置和路由守卫

#### src/stores/
Pinia 状态管理：
- **`user.ts`**: 用户状态管理，包含登录状态和用户信息

#### src/types/
TypeScript 类型定义：
- **`dashboard.ts`**: 仪表板相关类型定义
- **`echarts.ts`**: ECharts 图表相关类型定义

#### src/utils/
工具函数库：
- **`http.ts`**: Axios HTTP 请求封装和拦截器配置

#### src/views/
页面视图组件：
- **`Login/`**: 用户登录页面，支持账号密码登录
- **`Dashboard/`**: 经营驾驶舱，展示 KPI 和核心业务指标
- **`Analysis/`**: 智能分析页面，提供 AI 问答和自然语言查询
- **`Reports/`**: 报表中心，支持数据导出和自定义报表
- **`Operations/`**: 业务操作页面，处理日常业务数据
- **`Settings/`**: 系统设置页面，用户配置和偏好设置

### figma_source/ Figma 设计源代码目录

包含基于 React 的 Figma 设计实现，用于原型设计和界面验证：
- 完整的组件库和页面实现
- 模拟数据和交互逻辑
- 可以作为前端开发的参考和原型验证工具

## 🔧 开发指南

### 后端开发

1. **安装依赖**:
```bash
cd backend
pip install -r requirements.txt
```

2. **运行开发服务器**:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

3. **数据库迁移** (如需要):
```bash
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 前端开发

1. **安装依赖**:
```bash
cd frontend
npm install
```

2. **运行开发服务器**:
```bash
npm run dev
```

3. **构建生产版本**:
```bash
npm run build
```

## 🔒 安全配置

### 环境变量
- **`DASHSCOPE_API_KEY`**: 阿里百炼 API 密钥，必须从环境变量读取
- **`DATABASE_URL`**: 数据库连接字符串
- **`REDIS_URL`**: Redis 连接字符串

### 数据安全
- 使用 Row-Level Security (RLS) 实现数据行级权限控制
- 管理员可查看所有数据
- 分公司经理只能查看本分公司数据
- 普通员工仅查看个人数据

## 📊 数据模型

### 核心视图
- **`view_sales_analysis`**: 销售分析视图，包含订单、销售、客户等信息
- **`view_inventory_snapshot`**: 库存快照视图，实时库存状态
- **`view_finance_flow`**: 财务流水视图，应收应付等财务数据

### 维度字段
- 分公司、部门、职员、仓库、往来单位、地区、商品

### 指标字段
- 销售额、成本、毛利、费用发生额、往来余额、库存数量/金额

## 🤖 AI 功能说明

### Vanna.ai 集成
- **SQL 生成**: 将自然语言问题转换为准确的 SQL 查询
- **上下文学习**: 通过训练数据字典和示例问答提高准确性
- **缓存优化**: Redis 缓存减少重复查询的 Token 消耗

### 图表智能推荐
根据查询结果特征自动推荐最适合的图表类型：
- **时间序列数据** → 折线图
- **占比分析** → 饼图
- **对比分析** → 柱状图

## 📈 性能优化

- **异步处理**: 所有 API 端点使用 async/await
- **缓存策略**: Redis 缓存频繁查询结果
- **数据库优化**: 使用视图简化复杂查询
- **前端优化**: 组件懒加载、图表按需渲染

## 🔍 监控和调试

### 日志
- 后端使用 Loguru 进行结构化日志记录
- 前端集成 Vue DevTools 进行调试

### API 文档
- 自动生成的 OpenAPI 文档: `/docs`
- ReDoc 文档: `/redoc`

## 🚀 部署说明

### 生产环境部署

1. **构建镜像**:
```bash
docker-compose -f docker-compose.prod.yml build
```

2. **部署服务**:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

3. **配置反向代理** (Nginx):
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📝 开发规范

### 代码风格
- **后端**: 遵循 PEP 8 规范
- **前端**: 遵循 Vue 3 Composition API + TypeScript 最佳实践
- **命名**: 使用英文命名，注释使用中文

### 提交规范
```
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式调整
refactor: 代码重构
test: 测试相关
chore: 构建过程或工具配置更新
```

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支: `git checkout -b feature/amazing-feature`
3. 提交更改: `git commit -m 'Add amazing feature'`
4. 推送分支: `git push origin feature/amazing-feature`
5. 提交 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系我们

如有问题或建议，请提交 Issue 或联系开发团队。

---

**最后更新**: 2025年1月5日
