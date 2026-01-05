# Vanna 2.0 集成文档

## 📋 概述

本文档记录了 DataPulse BI 系统与 Vanna 2.0 的集成过程、架构设计和使用方法。

### 集成状态
- **版本**: Vanna 2.0.1
- **LLM**: 阿里百炼通义千问 (qwen-plus)
- **数据库**: PostgreSQL 16 + pgvector 0.8.0
- **缓存**: Redis 7
- **状态**: ✅ 已完成集成

---

## 🏗️ 技术架构

### Vanna 2.0 核心组件

```
┌─────────────────────────────────────────────┐
│           Vanna 2.0 Agent                   │
├─────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐        │
│  │ LLM Service  │  │ Tool Registry│        │
│  │  (通义千问)   │  │   (工具注册)  │        │
│  └──────────────┘  └──────────────┘        │
│  ┌──────────────┐  ┌──────────────┐        │
│  │ Agent Memory │  │ User Resolver│        │
│  │   (学习机制)  │  │  (用户认证)   │        │
│  └──────────────┘  └──────────────┘        │
└─────────────────────────────────────────────┘
         ↓                    ↓
┌─────────────────┐  ┌─────────────────┐
│  PostgresRunner │  │  DemoAgentMemory│
│  (SQL 执行器)    │  │  (内存存储)      │
└─────────────────┘  └─────────────────┘
```

### 核心类说明

1. **OpenAILlmService**: LLM 服务层
   - 通过 OpenAI 兼容接口连接通义千问
   - 负责自然语言理解和 SQL 生成

2. **PostgresRunner**: 数据库执行器
   - 执行 SQL 查询
   - 返回 DataFrame 格式的结果

3. **DemoAgentMemory**: Agent 记忆系统
   - 存储成功的问答对
   - 自动学习用户查询模式

4. **ToolRegistry**: 工具注册表
   - 注册可用的工具 (run_sql, save_memory 等)
   - 管理工具权限

---

## 📦 依赖安装

### Python 依赖 (requirements.txt)

```python
# AI 相关
vanna>=2.0.0
openai>=2.14.0
dashscope>=1.14.1

# 数据库
asyncpg>=0.29.0
psycopg2-binary>=2.9.9

# 数据处理
pandas>=2.1.0
```

### 安装 PGVector 扩展

```sql
-- 在 PostgreSQL 中执行
CREATE EXTENSION IF NOT EXISTS vector;

-- 验证安装
SELECT * FROM pg_extension WHERE extname = 'vector';
```

---

## ⚙️ 配置说明

### 环境变量配置 (.env)

```bash
# 阿里百炼 API Key (必须)
DASHSCOPE_API_KEY=sk-your-api-key-here

# 数据库配置
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/inventory_bi
DATABASE_URL_SYNC=postgresql+psycopg2://postgres:password@localhost:5432/inventory_bi

# 数据库连接详情 (Vanna 使用)
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=inventory_bi
DATABASE_USER=postgres
DATABASE_PASSWORD=password

# Redis 缓存
REDIS_URL=redis://localhost:6379/0

# 应用配置
DEBUG=True
SECRET_KEY=your-secret-key-change-in-production
```

### 获取阿里百炼 API Key

1. 访问 [阿里云百炼平台](https://bailian.console.aliyun.com/)
2. 注册/登录账号
3. 在控制台创建 API Key
4. 复制 API Key 到 `.env` 文件

---

## 🔧 核心代码实现

### 1. VannaService 初始化

```python
# backend/app/services/vanna_service.py

from vanna import Agent
from vanna.core.registry import ToolRegistry
from vanna.core.user import UserResolver, User, RequestContext
from vanna.tools import RunSqlTool
from vanna.integrations.openai import OpenAILlmService
from vanna.integrations.postgres import PostgresRunner
from vanna.integrations.local.agent_memory import DemoAgentMemory

class VannaService:
    def __init__(self):
        self.agent = None
        self.agent_memory = None
        self._initialize_connections()
    
    def _initialize_connections(self):
        # 1. 配置 LLM (通义千问)
        llm = OpenAILlmService(
            model="qwen-plus",
            api_key=os.getenv('DASHSCOPE_API_KEY'),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        
        # 2. 配置数据库工具
        db_url = f"postgresql://{os.getenv('DATABASE_USER')}:..."
        db_tool = RunSqlTool(
            sql_runner=PostgresRunner(connection_string=db_url)
        )
        
        # 3. 配置 Agent Memory
        self.agent_memory = DemoAgentMemory(max_items=1000)
        
        # 4. 配置用户认证
        class SimpleUserResolver(UserResolver):
            async def resolve_user(self, request_context: RequestContext) -> User:
                return User(
                    id="system_user",
                    email="system@inventory-bi.com",
                    group_memberships=["admin", "user"]
                )
        
        # 5. 注册工具
        tools = ToolRegistry()
        tools.register_local_tool(db_tool, access_groups=['admin', 'user'])
        
        # 6. 创建 Agent
        self.agent = Agent(
            llm_service=llm,
            tool_registry=tools,
            user_resolver=SimpleUserResolver(),
            agent_memory=self.agent_memory
        )
```

### 2. 查询执行

```python
async def ask_question(self, question: str, context: Dict[str, Any] = None):
    """处理用户自然语言问题"""
    
    # 创建 RequestContext
    request_context = RequestContext(
        cookies={},
        headers={},
        remote_addr="127.0.0.1",
        metadata=context or {}
    )
    
    # 发送消息并收集结果
    result_components = []
    async for component in self.agent.send_message(
        request_context=request_context,
        message=question
    ):
        result_components.append(component)
    
    # 解析结果 (从 rich_component 中提取)
    for component in result_components:
        dump = component.model_dump()
        if 'rich_component' in dump:
            rich = dump['rich_component']
            # 提取 DataFrame (在 rows + columns 中)
            if 'rows' in rich and 'columns' in rich:
                data_df = pd.DataFrame(rich['rows'], columns=rich['columns'])
                # ... 处理数据
```

### 3. 数据类型转换

```python
# 处理特殊类型 (Decimal, datetime, NaN)
from decimal import Decimal

for row in rows:
    for key, value in row.items():
        if pd.isna(value):
            row[key] = None
        elif isinstance(value, Decimal):
            row[key] = float(value)  # Decimal → float
        elif hasattr(value, 'isoformat'):
            row[key] = str(value)    # datetime → string
```

---

## 🚀 使用方法

### 1. 启动服务

```bash
# 1. 启动 Docker 容器 (PostgreSQL + Redis)
docker-compose up -d

# 2. 配置环境变量
# 编辑 backend/.env 文件，添加 DASHSCOPE_API_KEY

# 3. 安装 PGVector 扩展
docker exec -it datapulse_bi_db psql -U postgres -d inventory_bi -c "CREATE EXTENSION IF NOT EXISTS vector;"

# 4. 启动后端服务
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 测试 API

```bash
# 测试智能问答接口
curl -X POST "http://localhost:8000/api/v1/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "各分公司的销售业绩排名?"
  }'
```

### 3. API 响应格式

```json
{
  "answer_text": "根据销售数据，各分公司的业绩排名如下：\n1. 北京总公司 - 销售额：53,446,387.28元\n2. 上海分公司 - 销售额：23,691,247.95元",
  "sql": "SELECT company_name, SUM(total_amount) as total_sales FROM biz_order o JOIN sys_department d ON o.salesman_id = d.id GROUP BY company_name ORDER BY total_sales DESC",
  "chart_type": "bar",
  "data": {
    "columns": ["company_name", "total_sales"],
    "rows": [
      {"company_name": "北京总公司", "total_sales": 53446387.28},
      {"company_name": "上海分公司", "total_sales": 23691247.95}
    ]
  }
}
```

---

## 📊 数据库视图配置

Vanna 2.0 需要访问以下 BI 分析视图:

### 核心视图列表

1. **view_bi_sales_analysis** (销售分析)
   - company_name, salesman_name, region
   - product_name, category
   - sales_amount, gross_profit, gross_profit_rate
   - year, month

2. **view_bi_inventory_alert** (库存预警)
   - product_name, warehouse_name
   - current_stock, min_stock, stock_status

3. **view_bi_finance_monitor** (财务监控)
   - record_type, trans_amount, current_balance

4. **view_bi_purchase_analysis** (采购分析)
   - supplier_name, buyer_name, purchase_amount

这些视图在 `backend/app/db/init_views.sql` 中定义。

---

## 🎯 支持的查询类型

### 销售分析类
- "各分公司的销售业绩排名?"
- "2024年华东地区的销售额是多少?"
- "各业务员的销售业绩"

### 库存管理类
- "哪些商品的库存低于预警线?"
- "查询库存状况"
- "显示所有产品信息"

### 财务分析类
- "本月应收账款总额"
- "查询费用明细"

### 时间维度查询
- 支持按年、月、季度统计
- 自动识别时间范围

---

## 🔄 Agent Memory 学习机制

### 自动学习流程

```
用户提问 → Agent 生成 SQL → 执行成功 → 保存到 Memory
                                    ↓
                          下次相似问题 → 从 Memory 检索 → 更快响应
```

### Memory 存储内容

- **Question**: 用户原始问题
- **Tool Name**: 使用的工具 (run_sql)
- **Tool Args**: SQL 查询语句
- **Result**: 查询结果摘要
- **Success Flag**: 是否成功

---

## ⚠️ 常见问题

### 1. API Key 未配置

**错误**: `未配置 DASHSCOPE_API_KEY 环境变量`

**解决**:
```bash
# 在 backend/.env 中添加
DASHSCOPE_API_KEY=sk-your-api-key
```

### 2. 数据类型序列化错误

**错误**: `Object of type Decimal is not JSON serializable`

**解决**: 已在代码中处理 Decimal → float 转换

### 3. SQL 执行失败

**错误**: `relation "xxx" does not exist`

**原因**: Agent 生成的 SQL 引用了不存在的表

**解决**: Agent Memory 会自动学习正确的表名,多次查询后会改善

### 4. PGVector 扩展未安装

**错误**: `extension "vector" is not available`

**解决**:
```sql
CREATE EXTENSION vector;
```

---

## 📈 性能优化

### 1. Redis 缓存

查询结果会自动缓存到 Redis:

```python
# 缓存 key 格式
cache_key = f"ai:query:{question}:{json.dumps(context, sort_keys=True)}"

# 缓存时间: 1 小时
await redis_client.setex(cache_key, 3600, json.dumps(response))
```

### 2. Agent Memory 优化

- 最多存储 1000 个成功案例
- 自动清理旧的记录
- 支持相似度搜索

---

## 🔒 安全注意事项

### API Key 管理

✅ **推荐做法**:
```python
api_key = os.getenv('DASHSCOPE_API_KEY')  # 从环境变量读取
```

❌ **禁止做法**:
```python
api_key = "sk-xxxxx"  # 硬编码在代码中
```

### SQL 注入防护

Vanna 2.0 会自动处理 SQL 注入风险,但仍需注意:
- 不要直接拼接用户输入到 SQL
- 使用参数化查询
- 验证用户权限

---

## 📚 参考资源

- [Vanna 2.0 官方文档](https://vanna.ai/docs/)
- [阿里百炼文档](https://help.aliyun.com/zh/model-studio/)
- [PGVector 文档](https://github.com/pgvector/pgvector)

---

## 🎉 集成成果

### 已实现功能

✅ Vanna 2.0 Agent 初始化  
✅ 通义千问 LLM 集成  
✅ PostgreSQL 数据库连接  
✅ 自然语言转 SQL  
✅ DataFrame 数据解析  
✅ 类型转换 (Decimal/datetime)  
✅ Redis 缓存机制  
✅ Agent Memory 自动学习  

### 性能指标

- **首次查询**: ~3-5秒 (包含 LLM 推理)
- **缓存命中**: <100ms
- **SQL 准确率**: 逐步提升 (Agent Memory 学习中)

---

**文档版本**: v1.0  
**最后更新**: 2026-01-06  
**维护者**: DataPulse BI Team
