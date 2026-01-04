"""
ChatBI 智能问答接口
"""
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.services.vanna_service import vanna_service

router = APIRouter()

class ChatRequest(BaseModel):
    """聊天请求模型"""
    question: str
    context: Dict[str, Any] = None

class ChatResponse(BaseModel):
    """聊天响应模型"""
    sql: str
    data: list
    summary: str
    chart_type: str = "table"  # table, line, bar, pie

@router.post("/", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """
    AI 智能问答接口

    处理用户自然语言问题，返回 SQL 查询结果和图表推荐
    """
    try:
        # 调用 Vanna 服务生成 SQL
        result = await vanna_service.generate_sql(request.question, request.context)

        if not result:
            raise HTTPException(status_code=400, detail="无法生成有效的 SQL 查询")

        # 执行 SQL 查询
        data = await vanna_service.execute_sql(result["sql"])

        # 智能推荐图表类型
        chart_type = vanna_service.recommend_chart_type(data, request.question)

        return ChatResponse(
            sql=result["sql"],
            data=data,
            summary=result.get("summary", "查询完成"),
            chart_type=chart_type
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 查询失败: {str(e)}")

@router.get("/history")
async def get_chat_history():
    """
    获取聊天历史记录
    """
    # TODO: 实现聊天历史记录功能
    return {"history": []}
