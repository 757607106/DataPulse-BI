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
            # === 1. 准备示例问答对 (Question-SQL-Args pairs) ===
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
                    "args": {"sql": "SELECT * FROM biz_product LIMIT 20"}
                },
                {
                    "question": "各业务员的销售业绩",
                    "tool": "run_sql",
                    "args": {"sql": "SELECT salesman_name, SUM(sales_amount) as total_sales, SUM(gross_profit) as total_profit FROM view_bi_sales_analysis GROUP BY salesman_name ORDER BY total_sales DESC"}
                },
            ]
            
            # === 2. 保存到 Agent Memory ===
            logger.info(f"📚 正在添加 {len(training_examples)} 个示例到 Agent Memory...")
            
            for idx, example in enumerate(training_examples, 1):
                try:
                    # 使用 Vanna 2.0 的 Agent Memory save_tool_usage 方法
                    await self.agent_memory.save_tool_usage(
                        question=example["question"],
                        tool_name=example["tool"],
                        tool_args=example["args"],
                        result="成功查询数据",
                        is_correct=True
                    )
                    logger.info(f"  ✅ [{idx}/{len(training_examples)}] {example['question'][:30]}...")
                except Exception as e:
                    logger.warning(f"  ⚠️  [{idx}/{len(training_examples)}] 保存失败: {e}")
            
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
                message=question
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
                            # 记录包含表格数据的文本
                            if '\n' in text and len(text) > 50:
                                logger.info(f"📝 [{idx}] 文本内容(前200字符): {text[:200]}")
                            # 如果文本包含表格数据,尝试解析
                            if '\n' in text and ('|' in text or '\t' in text):
                                try:
                                    # 尝试作为 CSV 解析
                                    from io import StringIO
                                    df_temp = pd.read_csv(StringIO(text), sep='\t', error_bad_lines=False)
                                    if not df_temp.empty and data_df is None:
                                        data_df = df_temp
                                        logger.info(f"✅ [{idx}] 从文本解析到 DataFrame, shape: {data_df.shape}")
                                except:
                                    pass
                            answer_text += text + " "
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
        """智能推荐图表类型"""
        if df.empty:
            return "table"
        
        question_lower = question.lower()
        columns = df.columns.tolist()
        
        time_keywords = ['趋势', '变化', '时间', '月份', '季度', '年度']
        has_time_col = any(col in ['year', 'month', 'date'] for col in columns)
        if any(kw in question_lower for kw in time_keywords) or has_time_col:
            return "line"
        
        ratio_keywords = ['占比', '比例', '分布', '份额']
        if any(kw in question_lower for kw in ratio_keywords) and len(df) <= 10:
            return "pie"
        
        compare_keywords = ['排名', '对比', 'top', '前几', '最多', '最少']
        if any(kw in question_lower for kw in compare_keywords):
            return "bar"
        
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
