"""
ChatBI 智能问答接口 - 基于 Vanna + 通义千问
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from loguru import logger

from app.services.vanna_service import vanna_service

router = APIRouter()


class ChatRequest(BaseModel):
    """聊天请求模型"""
    question: str
    context: Optional[Dict[str, Any]] = None


class ChatDataResponse(BaseModel):
    """数据响应格式"""
    columns: List[str]
    rows: List[Dict[str, Any]]


class ChatResponse(BaseModel):
    """聊天响应模型"""
    answer_text: str  # AI 自然语言回答
    sql: str  # 生成的 SQL
    chart_type: str  # 推荐的图表类型: table, line, bar, pie, error, empty
    data: ChatDataResponse  # 数据


@router.post("/", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """
    AI 智能问答接口

    处理用户自然语言问题,返回 SQL 查询结果和图表推荐
    
    示例请求:
    ```json
    {
        "question": "2024年华东地区的销售额是多少?",
        "context": {
            "user_dept": "销售部",
            "user_region": "华东"
        }
    }
    ```
    
    返回格式:
    ```json
    {
        "answer_text": "根据您的问题...",
        "sql": "SELECT ...",
        "chart_type": "bar",
        "data": {
            "columns": ["region", "total_sales"],
            "rows": [{"region": "华东", "total_sales": 1000000}]
        }
    }
    ```
    """
    try:
        logger.info(f"📥 收到问题: {request.question}")
        
        # 调用 Vanna 服务处理问题
        result = await vanna_service.ask_question(request.question, request.context)
        
        if not result:
            raise HTTPException(
                status_code=500, 
                detail="AI 服务返回空结果,请稍后重试"
            )
        
        logger.info(f"✅ 查询成功,图表类型: {result.get('chart_type')}")
        
        return ChatResponse(
            answer_text=result.get("answer_text", ""),
            sql=result.get("sql", ""),
            chart_type=result.get("chart_type", "table"),
            data=ChatDataResponse(
                columns=result.get("data", {}).get("columns", []),
                rows=result.get("data", {}).get("rows", [])
            )
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ AI 查询失败: {e}")
        import traceback
        traceback.print_exc()
        
        raise HTTPException(
            status_code=500, 
            detail=f"AI 查询失败: {str(e)}"
        )


@router.get("/history")
async def get_chat_history():
    """
    获取聊天历史记录
    
    TODO: 实现聊天历史记录功能
    - 从数据库或 Redis 读取用户的历史问答
    - 支持分页
    - 支持按时间过滤
    """
    return {
        "history": [],
        "total": 0
    }


@router.get("/suggestions")
async def get_question_suggestions():
    """
    获取问题建议
    
    返回一些常见的示例问题,帮助用户快速上手
    """
    suggestions = [
        {
            "category": "销售分析",
            "questions": [
                "2024年华东地区的销售额是多少?",
                "各分公司的销售业绩排名?",
                "张三业务员在电子产品类的毛利率是多少?",
                "最近三个月的销售趋势如何?"
            ]
        },
        {
            "category": "库存管理",
            "questions": [
                "哪些商品的库存低于预警线?",
                "电子产品类的总库存价值是多少?",
                "上海仓库有哪些商品库存为0?"
            ]
        },
        {
            "category": "财务分析",
            "questions": [
                "北京分公司本月的费用总额是多少?",
                "华南地区客户的应收账款余额是多少?",
                "差旅费支出最多的部门是哪个?"
            ]
        },
        {
            "category": "采购分析",
            "questions": [
                "2024年从哪个供应商采购最多?",
                "华东地区供应商的采购金额是多少?"
            ]
        }
    ]
    
    return {"suggestions": suggestions}
