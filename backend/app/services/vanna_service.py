"""
Vanna AI 服务模块
"""
import asyncio
from typing import Dict, Any, List, Optional
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import json

from app.core.config import settings

class VannaService:
    """Vanna AI 服务类"""

    def __init__(self):
        self.redis_client = None
        self.db_engine = None
        self.db_session = None

    async def initialize(self):
        """初始化服务"""
        # 初始化 Redis 连接
        self.redis_client = redis.from_url(settings.redis_url)

        # 初始化数据库连接
        self.db_engine = create_async_engine(
            settings.database_url,
            echo=settings.debug,
            future=True
        )

        # 创建会话工厂
        self.db_session = sessionmaker(
            self.db_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # ===== 训练 Vanna AI 模型 =====
        # TODO: 集成真实的 Vanna.ai API 进行训练
        # 这里为训练逻辑预留接口
        await self._train_ai_models()

    async def generate_sql(self, question: str, context: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        生成 SQL 查询

        Args:
            question: 用户的问题
            context: 上下文信息

        Returns:
            包含 SQL 和相关信息的字典
        """
        # 检查缓存
        cache_key = f"sql:{question}:{json.dumps(context or {}, sort_keys=True)}"
        cached_result = await self.redis_client.get(cache_key)

        if cached_result:
            return json.loads(cached_result)

        try:
            # TODO: 集成 Vanna.ai 和阿里百炼 API
            # 这里是模拟实现
            sql = self._mock_generate_sql(question, context)

            result = {
                "sql": sql,
                "question": question,
                "context": context,
                "generated_at": "2024-01-01T00:00:00Z"
            }

            # 缓存结果 (1小时)
            await self.redis_client.setex(cache_key, 3600, json.dumps(result))

            return result

        except Exception as e:
            print(f"SQL 生成失败: {e}")
            return None

    async def execute_sql(self, sql: str) -> List[Dict[str, Any]]:
        """
        执行 SQL 查询

        Args:
            sql: SQL 查询语句

        Returns:
            查询结果列表
        """
        async with self.db_session() as session:
            try:
                result = await session.execute(sql)
                rows = result.fetchall()

                # 转换为字典列表
                columns = result.keys()
                data = [dict(zip(columns, row)) for row in rows]

                return data

            except Exception as e:
                print(f"SQL 执行失败: {e}")
                raise

    def recommend_chart_type(self, data: List[Dict[str, Any]], question: str) -> str:
        """
        推荐图表类型

        Args:
            data: 查询结果数据
            question: 原始问题

        Returns:
            图表类型: table, line, bar, pie
        """
        if not data:
            return "table"

        # 简单的图表推荐逻辑
        question_lower = question.lower()

        # 时间趋势相关的问题推荐折线图
        if any(keyword in question_lower for keyword in ["趋势", "变化", "时间", "月份", "季度", "年度"]):
            return "line"

        # 占比、分布相关的问题推荐饼图
        if any(keyword in question_lower for keyword in ["占比", "比例", "分布", "份额"]):
            return "pie"

        # 对比、排名相关的问题推荐柱状图
        if any(keyword in question_lower for keyword in ["排名", "对比", "top", "前几"]):
            return "bar"

        # 默认返回表格
        return "table"

    def build_report_sql(self, request) -> str:
        """
        构建报表查询 SQL

        Args:
            request: 报表请求对象

        Returns:
            SQL 查询语句
        """
        # 基础查询
        base_query = """
        SELECT
            {dimensions},
            {metrics}
        FROM view_sales_analysis
        WHERE 1=1
        {filters}
        {group_by}
        {order_by}
        {limit}
        """

        # 构建维度字段
        dimensions = ", ".join(request.dimensions) if request.dimensions else "*"

        # 构建指标字段
        metrics = ", ".join(request.metrics) if request.metrics else ""

        # 构建筛选条件
        filters = ""
        if request.filters:
            filter_conditions = []
            for key, value in request.filters.items():
                if isinstance(value, list):
                    values_str = ', '.join([f"'{v}'" for v in value])
                    filter_conditions.append(f"{key} IN ({values_str})")
                else:
                    filter_conditions.append(f"{key} = '{value}'")
            filters = " AND " + " AND ".join(filter_conditions)

        # 构建分组
        group_by = f"GROUP BY {', '.join(request.group_by)}" if request.group_by else ""

        # 构建排序
        order_by = f"ORDER BY {request.order_by}" if request.order_by else ""

        # 构建限制
        limit = f"LIMIT {request.limit}" if request.limit else ""

        return base_query.format(
            dimensions=dimensions,
            metrics=metrics,
            filters=filters,
            group_by=group_by,
            order_by=order_by,
            limit=limit
        )

    def calculate_summary(self, data: List[Dict[str, Any]], metrics: List[str]) -> Dict[str, Any]:
        """
        计算汇总数据

        Args:
            data: 数据列表
            metrics: 指标字段列表

        Returns:
            汇总结果字典
        """
        if not data or not metrics:
            return {}

        summary = {}
        for metric in metrics:
            values = [row.get(metric, 0) for row in data if row.get(metric) is not None]
            if values:
                summary[f"{metric}_sum"] = sum(values)
                summary[f"{metric}_avg"] = sum(values) / len(values)
                summary[f"{metric}_min"] = min(values)
                summary[f"{metric}_max"] = max(values)

        return summary

    async def get_dashboard_kpis(self) -> Dict[str, Any]:
        """
        获取仪表板 KPI 数据

        Returns:
            KPI 指标字典
        """
        # TODO: 实现实际的 KPI 计算逻辑
        return {
            "total_sales": 1250000.00,
            "total_orders": 1250,
            "avg_order_value": 1000.00,
            "inventory_turnover": 8.5
        }

    async def get_dashboard_charts(self) -> List[Dict[str, Any]]:
        """
        获取仪表板图表数据

        Returns:
            图表数据列表
        """
        # TODO: 实现实际的图表数据查询逻辑
        return [
            {
                "id": "sales_trend",
                "type": "line",
                "title": "销售趋势",
                "data": []  # 实际数据
            },
            {
                "id": "category_sales",
                "type": "pie",
                "title": "品类销售占比",
                "data": []  # 实际数据
            }
        ]

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
        # 训练销售分析视图
        # await vanna.train(
        #     ddl="""
        #     CREATE VIEW view_bi_sales_analysis AS ...
        #     字段说明:
        #     - company_name: 分公司名称
        #     - salesman_name: 业务员姓名
        #     - partner_name: 客户名称
        #     - region: 客户地区 (华东/华北/华南等)
        #     - product_name: 商品名称
        #     - category: 商品分类
        #     - sales_amount: 销售额
        #     - gross_profit: 毛利
        #     - gross_profit_rate: 毛利率
        #     """
        # )
        
        # 训练财务监控视图
        # await vanna.train(
        #     ddl="""
        #     CREATE VIEW view_bi_finance_monitor AS ...
        #     字段说明:
        #     - record_type: 记录类型 (receivable应收/payable应付/expense费用)
        #     - trans_amount: 交易金额
        #     - current_balance: 当前余额
        #     - expense_category: 费用科目
        #     """
        # )
        
        # 训练库存预警视图
        # await vanna.train(
        #     ddl="""
        #     CREATE VIEW view_bi_inventory_alert AS ...
        #     字段说明:
        #     - product_name: 商品名称
        #     - current_stock: 当前库存
        #     - min_stock: 最低库存预警线
        #     - stock_status: 库存状态 (缺货/库存不足/正常/库存充足)
        #     """
        # )
        
        print("✅ Vanna AI 模型训练完成 (当前为模拟模式)")

    def _mock_generate_sql(self, question: str, context: Dict[str, Any] = None) -> str:
        """
        模拟 SQL 生成 (临时实现)

        在实际项目中，这里会调用 Vanna.ai 和阿里百炼 API
        """
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

        elif "库存" in question_lower:
            return """
            SELECT
                product_name,
                current_stock,
                min_stock,
                warehouse_name,
                stock_status
            FROM view_bi_inventory_alert
            WHERE current_stock < min_stock OR current_stock <= 0
            ORDER BY 
                CASE stock_status
                    WHEN '缺货' THEN 1
                    WHEN '库存不足' THEN 2
                    ELSE 3
                END
            LIMIT 20
            """

        elif "费用" in question_lower or "应收" in question_lower or "应付" in question_lower:
            return """
            SELECT
                company_name,
                dept_name,
                record_type,
                expense_category,
                SUM(trans_amount) as total_amount
            FROM view_bi_finance_monitor
            WHERE trans_date >= CURRENT_DATE - INTERVAL '3 months'
            GROUP BY company_name, dept_name, record_type, expense_category
            ORDER BY total_amount DESC
            """

        else:
            return """
            SELECT * FROM view_bi_sales_analysis LIMIT 100
            """

# 创建全局服务实例
vanna_service = VannaService()
