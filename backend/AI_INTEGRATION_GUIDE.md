# P1 阶段：Vanna AI 集成完成指南

## 🎉 完成内容

### 1. 依赖添加 ✅
- `vanna[postgres]` - Vanna 核心库 (PostgreSQL 版本)
- `dashscope` - 阿里百炼(通义千问) SDK
- `pgvector` - PostgreSQL 向量扩展支持

### 2. VannaService 重写 ✅
**文件**: `backend/app/services/vanna_service.py`

**核心功能**:
- ✅ 继承 `VannaBase` + `PG_VectorStore` + `OpenAI_Chat`
- ✅ 使用 PostgreSQL + pgvector 作为向量存储
- ✅ 通过 OpenAI 兼容接口连接通义千问
- ✅ 自动训练 4 个核心视图 DDL
- ✅ 内置 8+ 个典型问答对训练
- ✅ Redis 缓存优化
- ✅ 智能图表类型推荐
- ✅ 自然语言回答生成

### 3. 训练脚本 ✅
**文件**: `backend/scripts/train_ai.py`

**功能**: 初始化和训练 Vanna AI 系统

### 4. Chat API 重构 ✅
**文件**: `backend/app/api/v1/endpoints/chat.py`

**新增接口**:
- `POST /api/v1/chat/` - AI 问答主接口
- `GET /api/v1/chat/suggestions` - 获取示例问题

---

## 🚀 启动步骤

### 步骤 1: 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 步骤 2: 配置环境变量

在 `backend/.env` 文件中添加:

```env
# 阿里百炼 API Key (必须)
DASHSCOPE_API_KEY=sk-your-api-key-here

# 数据库配置
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=inventory_bi
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres123

# 自动生成的连接字符串
DATABASE_URL=postgresql+asyncpg://postgres:postgres123@localhost:5432/inventory_bi
DATABASE_URL_SYNC=postgresql+psycopg2://postgres:postgres123@localhost:5432/inventory_bi

# Redis
REDIS_URL=redis://localhost:6379/0
```

> **重要**: 请从阿里云控制台获取你的 `DASHSCOPE_API_KEY`

### 步骤 3: 安装 PGVector 扩展

连接到 PostgreSQL 数据库:

```bash
psql -U postgres -d inventory_bi
```

执行:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 步骤 4: 训练 AI 系统

**首次运行前必须执行训练**:

```bash
cd backend
python scripts/train_ai.py
```

预期输出:
```
================================================================================
🚀 Vanna AI 训练脚本启动
================================================================================
✅ 配置检查通过
   - 数据库: postgresql+psycopg2://...
   - Redis: redis://localhost:6379/0
   - API Key: sk-abc123***

🤖 开始训练 Vanna AI 系统...
✅ DDL 训练完成
✅ 训练了 8 个问答对
✅ 业务规则训练完成
🎉 Vanna AI 训练完成！
```

### 步骤 5: 启动后端服务

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🧪 测试 API

### 1. 测试问答接口

**请求**:
```bash
curl -X POST http://localhost:8000/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "question": "2024年华东地区的销售额是多少?"
  }'
```

**响应示例**:
```json
{
  "answer_text": "根据您的问题「2024年华东地区的销售额是多少?」，查询到 1 条数据。数据呈现为对比排名，建议查看柱状图。",
  "sql": "SELECT SUM(sales_amount) as total_sales FROM view_bi_sales_analysis WHERE year = 2024 AND region = '华东'",
  "chart_type": "bar",
  "data": {
    "columns": ["total_sales"],
    "rows": [{"total_sales": 1250000.00}]
  }
}
```

### 2. 获取问题建议

```bash
curl http://localhost:8000/api/v1/chat/suggestions
```

---

## 📊 内置训练的问答对

### 销售分析场景
- "2024年华东地区的销售额是多少?"
- "张三业务员在电子产品类的毛利率是多少?"
- "各分公司的销售业绩排名?"

### 库存管理场景
- "哪些商品的库存低于预警线?"
- "电子产品类的总库存价值是多少?"

### 财务分析场景
- "北京分公司本月的费用总额是多少?"
- "华南地区客户的应收账款余额是多少?"

### 采购分析场景
- "2024年从哪个供应商采购最多?"

---

## 🔧 故障排查

### 问题 1: `ModuleNotFoundError: No module named 'vanna'`
**解决**: 
```bash
pip install vanna[postgres] dashscope pgvector
```

### 问题 2: 训练失败 "未配置 DASHSCOPE_API_KEY"
**解决**: 
1. 检查 `.env` 文件是否存在
2. 确认 `DASHSCOPE_API_KEY` 已正确设置
3. 重启终端或重新加载环境变量

### 问题 3: PGVector 扩展未安装
**错误**: `ERROR: extension "vector" does not exist`
**解决**:
```bash
# Ubuntu/Debian
sudo apt install postgresql-15-pgvector

# macOS
brew install pgvector

# 然后在数据库中执行
CREATE EXTENSION vector;
```

### 问题 4: AI 返回错误的 SQL
**解决**: 
1. 重新训练: `python scripts/train_ai.py`
2. 添加更多问答对到 `vanna_service.py` 的 `qa_pairs` 列表
3. 检查视图是否正确创建: `SELECT * FROM view_bi_sales_analysis LIMIT 1;`

---

## 🎯 下一步

- [ ] 前端集成 Chat 界面
- [ ] 添加行级权限过滤 (context)
- [ ] 实现聊天历史记录
- [ ] 优化图表渲染逻辑
- [ ] 添加更多训练数据

---

## 📝 技术架构

```
┌─────────────┐
│   用户提问   │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│  FastAPI Chat Endpoint          │
│  /api/v1/chat/                  │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  VannaService.ask_question()    │
│  - Redis 缓存检查               │
│  - 生成 SQL (Vanna + 通义千问)  │
│  - 执行 SQL                     │
│  - 推荐图表类型                 │
│  - 生成自然语言回答             │
└────────────┬────────────────────┘
             │
    ┌────────┴─────────┐
    │                  │
    ▼                  ▼
┌──────────┐    ┌─────────────┐
│ PGVector │    │  通义千问    │
│ (向量库)  │    │  (LLM)      │
└──────────┘    └─────────────┘
```

---

**完成时间**: 2026-01-05
**版本**: P1 - 真实 AI 集成
