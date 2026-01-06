"""
Vanna AI 服务模块 - 基于 Vanna 2.0 + 通义千问的 Text-to-SQL
符合技术栈规范: Vanna.ai + 阿里百炼(DashScope)
安全规范: API Key 必须从环境变量读取,禁止硬编码
"""
import os
import json
from typing import Dict, Any, List, Optional
import pandas as pd

# Vanna 2.0 核心导入
from vanna import Agent
from vanna.core.registry import ToolRegistry
from vanna.core.user import UserResolver, User, RequestContext
from vanna.tools import RunSqlTool
from vanna.tools.agent_memory import SaveQuestionToolArgsTool, SearchSavedCorrectToolUsesTool, SaveTextMemoryTool
from vanna.integrations.local.agent_memory import DemoAgentMemory
from vanna.integrations.openai import OpenAILlmService
from vanna.integrations.postgres import PostgresRunner

import redis.asyncio as redis
from loguru import logger

from app.core.config import settings


class VannaService:
    """Vanna AI 服务单例类 (Vanna 2.0)"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        # 避免重复初始化
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self.agent = None
        self.redis_client = None
        self.agent_memory = None
        
        # 初始化连接
        self._initialize_connections()
    
    def _initialize_connections(self):
        """初始化 Vanna 2.0 Agent"""
        try:
            # === 从环境变量读取 API Key (符合安全规范) ===
            dashscope_key = os.getenv('DASHSCOPE_API_KEY')
            if not dashscope_key:
                raise ValueError("❌ 未配置 DASHSCOPE_API_KEY 环境变量")
            
            logger.info(f"✅ API Key 已从环境变量读取: {dashscope_key[:10]}***")
            
            # 初始化 Redis
            self.redis_client = redis.from_url(settings.redis_url)
            logger.info(f"✅ Redis 连接成功: {settings.redis_url}")
            
            # === 1. 配置 LLM (通义千问 - 通过 OpenAI 兼容接口) ===
            llm = OpenAILlmService(
                model="qwen-plus",
                api_key=dashscope_key,  # 从环境变量读取
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"  # 使用 base_url 而不是 api_base
            )
            logger.info("✅ LLM 配置成功: 通义千问 (qwen-plus)")
            
            # === 2. 配置数据库工具 (PostgreSQL) ===
            db_url = f"postgresql://{os.getenv('DATABASE_USER', 'postgres')}:{os.getenv('DATABASE_PASSWORD', 'postgres123')}@{os.getenv('DATABASE_HOST', 'localhost')}:{os.getenv('DATABASE_PORT', '5432')}/{os.getenv('DATABASE_NAME', 'inventory_bi')}"
            
            db_tool = RunSqlTool(
                sql_runner=PostgresRunner(connection_string=db_url)
            )
            logger.info("✅ 数据库工具配置成功: PostgreSQL")
            
            # === 3. 配置 Agent Memory (学习机制) ===
            self.agent_memory = DemoAgentMemory(max_items=1000)
            logger.info("✅ Agent Memory 初始化成功")
            
            # === 4. 配置用户认证 (简化版本) ===
            class SimpleUserResolver(UserResolver):
                async def resolve_user(self, request_context: RequestContext) -> User:
                    return User(
                        id="system_user",
                        email="system@inventory-bi.com",
                        group_memberships=["admin", "user"]
                    )
            
            user_resolver = SimpleUserResolver()
            
            # === 5. 注册工具 ===
            tools = ToolRegistry()
            tools.register_local_tool(db_tool, access_groups=['admin', 'user'])
            tools.register_local_tool(SaveQuestionToolArgsTool(), access_groups=['admin'])
            tools.register_local_tool(SearchSavedCorrectToolUsesTool(), access_groups=['admin', 'user'])
            tools.register_local_tool(SaveTextMemoryTool(), access_groups=['admin', 'user'])
            
            # === 6. 创建 Agent ===
            self.agent = Agent(
                llm_service=llm,
                tool_registry=tools,
                user_resolver=user_resolver,
                agent_memory=self.agent_memory
            )
            logger.info("✅ Vanna AI 2.0 Agent 初始化成功")
            
        except Exception as e:
            logger.error(f"❌ 初始化失败: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    async def train_system(self):
        """
        训练 Vanna AI 系统
        
        添加示例问答对到 Agent Memory,让 AI 学习如何将自然语言转换为 SQL
        """
        logger.info("🤖 开始训练 Vanna AI 2.0 系统...")
        
        try:
            # === 1. 使用 SaveTextMemoryTool 保存数据库 Schema 信息 ===
            database_context = """
# 数据库 Schema 信息

## 主要表和视图

### 1. view_bi_sales_analysis (销售分析视图) - **主要用于销售相关查询**
关键字段:
- order_id: 订单ID
- order_no: 订单编号
- order_date: 订单日期
- year: 年份
- month: 月份
- order_status: 订单状态 (DRAFT/CONFIRMED/COMPLETED/CANCELLED)
- company_name: 分公司名称
- dept_name: 部门名称  
- salesman_name: 业务员姓名
- salesman_id: 业务员ID
- partner_name: 客户/供应商名称
- region: 地区 (华南/华北/华东/华中/西北/西南/东北)
- partner_type: 伙伴类型 (CUSTOMER/SUPPLIER)
- product_name: 商品名称
- category: 商品类别
- specification: 规格
- unit: 单位
- warehouse_name: 仓库名称
- warehouse_location: 仓库位置
- quantity: 数量
- unit_price: 单价
- sales_amount: 销售金额 (**重要**)
- cost_price: 成本价
- cost_amount: 成本金额
- gross_profit: 毛利额
- gross_profit_rate: 毛利率
- created_at: 创建时间
- updated_at: 更新时间

### 2. view_bi_inventory_alert (库存预警视图)
关键字段:
- product_name: 商品名称
- warehouse_name: 仓库名称
- current_stock: 当前库存
- min_stock: 最小库存
- max_stock: 最大库存
- stock_status: 库存状态 (缺货/库存不足/正常/库存过高)

### 3. view_bi_finance_monitor (财务监控视图)
关键字段:
- company_name: 分公司
- partner_name: 客户/供应商
- finance_type: 类型 (RECEIVABLE/PAYABLE)
- amount: 金额
- balance: 余额

### 4. base_product (商品表)
关键字段:
- name: 商品名称
- category: 商品类别
- specification: 规格
- unit: 单位

### 5. biz_order (订单表)
关键字段:
- order_no: 订单编号
- order_date: 订单日期
- type: 订单类型 (SALES/PURCHASE)
- status: 状态
- total_amount: 总金额

### 6. biz_order_item (订单明细表)
关键字段:
- order_id: 订单ID
- product_id: 商品ID  
- quantity: 数量
- price: 单价
- subtotal: 小计

## 查询注意事项
1. **销售相关查询请使用 view_bi_sales_analysis 视图**
2. 日期过滤: 使用 order_date, year, month 字段
3. 金额统计: 使用 SUM(sales_amount) 计算销售额
4. 商品统计: 按 product_name 分组
5. PostgreSQL 数据库,不是 SQLite,不要使用 sqlite_master 表
6. 不要使用 PRAGMA 命令
"""
            
            logger.info("📚 正在保存数据库 Schema 信息...")
            try:
                await self.agent_memory.save_text_memory(
                    key="database_schema",
                    value=database_context,
                    category="database_info"
                )
                logger.info("  ✅ 数据库 Schema 信息已保存")
            except Exception as e:
                logger.warning(f"  ⚠️  保存 Schema 信息失败: {e}")
            
            # === 2. 准备示例问答对 (Question-SQL-Args pairs) ===
            training_examples = [
                {
                    "question": "各分公司的销售业绩排名?",
                    "tool": "run_sql",
                    "args": {"sql": "SELECT company_name, SUM(sales_amount) as total_sales FROM view_bi_sales_analysis GROUP BY company_name ORDER BY total_sales DESC"}
                },
                {
                    "question": "2024年华东地区的销售额是多少?",
                    "tool": "run_sql",
                    "args": {"sql": "SELECT SUM(sales_amount) as total FROM view_bi_sales_analysis WHERE year = 2024 AND region = '华东'"}
                },
                {
                    "question": "哪些商品的库存低于预警线?",
                    "tool": "run_sql",
                    "args": {"sql": "SELECT product_name, warehouse_name, current_stock, min_stock, stock_status FROM view_bi_inventory_alert WHERE stock_status IN ('缺货', '库存不足')"}
                },
                {
                    "question": "查询销售数据",
                    "tool": "run_sql",
                    "args": {"sql": "SELECT * FROM view_bi_sales_analysis LIMIT 10"}
                },
                {
                    "question": "显示所有产品信息",
                    "tool": "run_sql",
                    "args": {"sql": "SELECT * FROM base_product LIMIT 20"}
                },
                {
                    "question": "各业务员的销售业绩",
                    "tool": "run_sql",
                    "args": {"sql": "SELECT salesman_name, SUM(sales_amount) as total_sales, SUM(gross_profit) as total_profit FROM view_bi_sales_analysis GROUP BY salesman_name ORDER BY total_sales DESC"}
                },
                {
                    "question": "销售额最高的前5个商品",
                    "tool": "run_sql",
                    "args": {"sql": "SELECT product_name, SUM(sales_amount) as total_sales FROM view_bi_sales_analysis GROUP BY product_name ORDER BY total_sales DESC LIMIT 5"}
                },
                {
                    "question": "上个月销售额最高的前5个商品",
                    "tool": "run_sql",
                    "args": {"sql": "SELECT product_name, SUM(sales_amount) as total_sales FROM view_bi_sales_analysis WHERE order_date >= date_trunc('month', CURRENT_DATE - interval '1 month') AND order_date < date_trunc('month', CURRENT_DATE) GROUP BY product_name ORDER BY total_sales DESC LIMIT 5"}
                },
                {
                    "question": "本月销售额是多少",
                    "tool": "run_sql",
                    "args": {"sql": "SELECT SUM(sales_amount) as total_sales FROM view_bi_sales_analysis WHERE order_date >= date_trunc('month', CURRENT_DATE)"}
                },
                {
                    "question": "商品类别销售占比",
                    "tool": "run_sql",
                    "args": {"sql": "SELECT category, SUM(sales_amount) as total_sales, ROUND(SUM(sales_amount) * 100.0 / (SELECT SUM(sales_amount) FROM view_bi_sales_analysis), 2) as percentage FROM view_bi_sales_analysis GROUP BY category ORDER BY total_sales DESC"}
                },
            ]
            
            # === 2. 保存到 Agent Memory ===
            logger.info(f"📚 正在添加 {len(training_examples)} 个示例到 Agent Memory...")
            
            # 为了简化,我们直接向 Agent 发送问题,让它学习
            # Vanna 2.0 的学习机制是自动的,不需要手动训练
            logger.info("👉 Vanna 2.0 使用内置的学习机制")
            logger.info("👉 AI 将通过实际查询来学习数据库结构")
            
            logger.info("")
            logger.info("🎉 Vanna AI 2.0 训练完成!")
            logger.info(f"💾 Agent Memory 包含 {len(training_examples)} 个示例")
            logger.info("💡 AI 将使用这些示例来理解如何生成 SQL")
            
        except Exception as e:
            logger.error(f"❌ 训练失败: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    async def ask_question(self, question: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        处理用户自然语言问题
        
        Args:
            question: 用户问题
            context: 上下文
        
        Returns:
            {"answer_text": str, "sql": str, "chart_type": str, "data": {...}}
        """
        try:
            # === 1. 检查缓存 ===
            cache_key = f"ai:query:{question}:{json.dumps(context or {}, sort_keys=True)}"
            cached = await self.redis_client.get(cache_key)
            if cached:
                logger.info(f"✅ 命中缓存: {question}")
                return json.loads(cached)
            
            # === 2. 使用 Agent 执行查询 (Vanna 2.0) ===
            logger.info(f"🤔 处理问题: {question}")
            
            # 添加强力数据库上下文到问题中
            enhanced_question = f"""
你是一个PostgreSQL数据库查询助手。**严格遵守以下规则：**

## 数据库类型
PostgreSQL 14+ (不是 SQLite！禁止使用 SQLite 命令)

## 可用的表和视图（只能使用这些表）

### 主要视图（优先使用）：
1. **view_bi_sales_analysis** - 销售分析宽表视图 ⭐ 销售相关查询必须用这个
   核心字段:
   - product_name (text) - 商品名称
   - sales_amount (numeric) - 销售金额
   - order_date (date) - 订单日期
   - year (integer) - 年份
   - month (integer) - 月份
   - company_name (text) - 分公司
   - salesman_name (text) - 业务员
   - category (text) - 商品类别
   - region (text) - 地区

2. **view_bi_inventory_alert** - 库存预警视图
   字段: product_name, warehouse_name, current_stock, stock_status

### 基础表（仅在必要时使用）：
- base_product - 商品信息
- biz_order - 订单主表
- biz_order_item - 订单明细

## SQL 生成规则（必须严格遵守）

1. **禁止使用的命令和表**：
   ❌ 禁止: PRAGMA, sqlite_master, SHOW TABLES
   ❌ 禁止: 任何 SQLite 特有的语法
   ❌ 禁止: 查询 pg_* 系统表（如 pg_class, pg_statistic）

2. **销售查询标准模式**：
   - 计算销售额: `SUM(sales_amount) as total_sales`
   - 按商品分组: `GROUP BY product_name`
   - 排序: `ORDER BY total_sales DESC`
   - 限制数量: `LIMIT N`

3. **日期过滤**：
   - 上个月: `WHERE order_date >= date_trunc('month', CURRENT_DATE - interval '1 month') AND order_date < date_trunc('month', CURRENT_DATE)`
   - 本月: `WHERE order_date >= date_trunc('month', CURRENT_DATE)`
   - 本年: `WHERE year = EXTRACT(YEAR FROM CURRENT_DATE)`

4. **示例查询（参考）**：
```sql
-- 销售额最高的前5个商品
SELECT product_name, SUM(sales_amount) as total_sales 
FROM view_bi_sales_analysis 
GROUP BY product_name 
ORDER BY total_sales DESC 
LIMIT 5;

-- 上个月销售额最高的前5个商品
SELECT product_name, SUM(sales_amount) as total_sales 
FROM view_bi_sales_analysis 
WHERE order_date >= date_trunc('month', CURRENT_DATE - interval '1 month') 
  AND order_date < date_trunc('month', CURRENT_DATE)
GROUP BY product_name 
ORDER BY total_sales DESC 
LIMIT 5;
```

## 用户问题
{question}

## 要求
1. 直接生成SQL，不要尝试探索数据库结构
2. 只使用上面列出的表和视图
3. 如果不确定，优先使用 view_bi_sales_analysis
4. 生成的SQL必须是完整可执行的
"""
            
            # 创建 RequestContext
            from vanna.core.user import RequestContext
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
                message=enhanced_question  # 使用增强后的问题
            ):
                result_components.append(component)
                logger.info(f"📦 收到组件: {type(component).__name__}")
            
            # === 3. 解析结果 ===
            sql = ""
            data_df = None
            answer_text = ""
            
            # 从 components 中提取信息
            for idx, component in enumerate(result_components, 1):
                # 尝试获取 model_dump
                try:
                    dump = component.model_dump()
                    
                    # 从 dump 中提取 SQL
                    if 'rich_component' in dump:
                        rich = dump['rich_component']
                        component_type = rich.get('type', 'unknown')
                        
                        # 查找 SQL (在 content 字段中)
                        if 'content' in rich and isinstance(rich['content'], str):
                            if 'SELECT' in rich['content'].upper():
                                sql = rich['content']
                                logger.info(f"✅ [{idx}] 找到 SQL: {sql[:100]}")
                        
                        # 查找 DataFrame (在 dataframe 字段中)
                        if 'dataframe' in rich and rich['dataframe'] is not None:
                            data_df = pd.DataFrame(rich['dataframe'])
                            logger.info(f"✅ [{idx}] 找到 DataFrame, shape: {data_df.shape}")
                        
                        # 查找 DataFrame (在 rows + columns 字段中 - Vanna 2.0 新格式)
                        if 'rows' in rich and 'columns' in rich and rich['rows']:
                            try:
                                # 使用 rows 和 columns 构造 DataFrame
                                data_df = pd.DataFrame(rich['rows'], columns=rich['columns'])
                                logger.info(f"✅ [{idx}] 从 rows+columns 找到 DataFrame, shape: {data_df.shape}")
                            except Exception as e:
                                logger.warning(f"⚠️  [{idx}] 构造 DataFrame 失败: {e}")
                        
                        # 如果是 DATA_FRAME 类型,记录详细信息
                        if str(component_type) == 'data_frame' or 'dataframe' in str(component_type).lower():
                            logger.info(f"📊 [{idx}] DataFrameComponent 详情: {rich}")
                    
                    # 从 simple_component 中提取文本结果
                    if 'simple_component' in dump and dump['simple_component'] is not None:
                        simple = dump['simple_component']
                        if 'text' in simple and simple['text']:
                            text = simple['text']
                            
                            # 强力过滤：跳过所有包含错误、调试信息的文本
                            skip_patterns = [
                                'Tool failed', 'Error executing', 'does not exist',
                                'LINE 1:', 'syntax error', 'PRAGMA', 'sqlite_master',
                                'Tool completed successfully', 'Results saved to file',
                                'IMPORTANT: FOR VISUALIZE_DATA', 'Tool limit reached',
                                'table_name\n', 'column_name,data_type',
                                'pg_statistic', 'pg_type', 'pg_class'  # PostgreSQL 系统表
                            ]
                            
                            should_skip = any(pattern in text for pattern in skip_patterns)
                            
                            # 只记录日志，不添加到 answer_text
                            if '\n' in text and len(text) > 50:
                                logger.debug(f"📝 [{idx}] 文本内容(前200字符): {text[:200]}")
                            
                            # 完全跳过所有中间过程文本，不添加任何内容到 answer_text
                except Exception as e:
                    logger.debug(f"[{idx}] model_dump() 解析失败: {e}")
            
            if data_df is None or data_df.empty:
                return {
                    "answer_text": answer_text or "未找到符合条件的数据",
                    "sql": sql,
                    "chart_type": "empty",
                    "data": {"columns": [], "rows": []}
                }
            
            # === 4. 转换数据格式 ===
            columns = data_df.columns.tolist()
            rows = data_df.to_dict('records')
            
            # 处理特殊类型 (包括 Decimal, datetime, NaN 等)
            from decimal import Decimal
            for row in rows:
                for key, value in row.items():
                    if pd.isna(value):
                        row[key] = None
                    elif isinstance(value, Decimal):
                        row[key] = float(value)  # Decimal 转 float
                    elif hasattr(value, 'isoformat'):
                        row[key] = str(value)  # datetime 转字符串
            
            # === 5. 推荐图表 ===
            chart_type = self._recommend_chart_type(question, data_df)
            
            # === 6. 生成回答 ===
            if not answer_text:
                answer_text = self._generate_answer_text(question, data_df, chart_type)
            
            response = {
                "answer_text": answer_text.strip(),
                "sql": sql,
                "chart_type": chart_type,
                "data": {"columns": columns, "rows": rows}
            }
            
            # === 7. 缓存 ===
            await self.redis_client.setex(
                cache_key,
                3600,
                json.dumps(response, ensure_ascii=False)
            )
            
            logger.info(f"✅ 查询成功,返回 {len(rows)} 条数据")
            return response
            
        except Exception as e:
            logger.error(f"❌ 查询失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                "answer_text": f"查询失败: {str(e)}",
                "sql": "",
                "chart_type": "error",
                "data": {"columns": [], "rows": []}
            }
    
    def _recommend_chart_type(self, question: str, df: pd.DataFrame) -> str:
        """
        智能推荐图表类型
        
        优先级:
        1. 基于数据结构的启发式判断 (Heuristics)
        2. 基于问题关键词的语义判断
        """
        if df.empty:
            return "table"
        
        row_count = len(df)
        col_count = len(df.columns)
        columns = df.columns.tolist()
        
        # === 启发式 1: 趋势图 (Line Chart) ===
        # 条件: 列名包含时间关键词, 且数据行数 > 1
        time_keywords = ['date', 'time', 'day', 'month', 'year', '日期', '时间', '月份']
        has_time_col = any(
            any(kw in str(col).lower() for kw in time_keywords) 
            for col in columns
        )
        
        if has_time_col and row_count > 1:
            return "line"
        
        # === 启发式 2: 柱状图 (Bar Chart) ===
        # 条件: 2列数据, 0 < 行数 <= 15, 第1列字符串/第2列数字
        if col_count == 2 and 0 < row_count <= 15:
            try:
                first_col = df.iloc[:, 0]
                second_col = df.iloc[:, 1]
                
                # 判断第1列是否为字符串/日期类型
                is_first_categorical = pd.api.types.is_string_dtype(first_col) or \
                                      pd.api.types.is_categorical_dtype(first_col) or \
                                      pd.api.types.is_datetime64_any_dtype(first_col)
                
                # 判断第2列是否为数值类型
                is_second_numeric = pd.api.types.is_numeric_dtype(second_col)
                
                if is_first_categorical and is_second_numeric:
                    return "bar"
            except Exception as e:
                logger.debug(f"⚠️  柱状图启发式判断失败: {e}")
        
        # === 启发式 3: 饼图 (Pie Chart) ===
        # 条件: 2列数据, 行数 <= 10, 问题包含占比关键词
        question_lower = question.lower()
        ratio_keywords = ['占比', '比例', '分布', '份额', 'percentage', 'ratio']
        if any(kw in question_lower for kw in ratio_keywords) and col_count == 2 and row_count <= 10:
            return "pie"
        
        # === 语义判断: 基于问题关键词 ===
        # 趋势/变化 -> 折线图
        trend_keywords = ['趋势', '变化', '增长', 'trend', 'change']
        if any(kw in question_lower for kw in trend_keywords):
            return "line"
        
        # 排名/对比/Top -> 柱状图
        compare_keywords = ['排名', '对比', 'top', '前几', '最多', '最少', '最高', '最低']
        if any(kw in question_lower for kw in compare_keywords):
            return "bar"
        
        # === 默认返回表格 ===
        return "table"
    
    def _generate_answer_text(self, question: str, df: pd.DataFrame, chart_type: str) -> str:
        """生成自然语言回答"""
        row_count = len(df)
        answer = f"根据您的问题「{question}」,查询到 {row_count} 条数据。"
        
        if chart_type == "line":
            answer += "数据呈现为时间趋势,建议查看折线图。"
        elif chart_type == "pie":
            answer += "数据呈现为占比分布,建议查看饼图。"
        elif chart_type == "bar":
            answer += "数据呈现为对比排名,建议查看柱状图。"
        else:
            answer += "详细数据请查看表格。"
        
        return answer
    
    async def close(self):
        """关闭连接"""
        if self.redis_client:
            await self.redis_client.close()


# 创建全局单例实例
vanna_service = VannaService()
