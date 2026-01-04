"""
聊天相关的 Pydantic 模型
"""
from typing import Dict, Any, Optional
from pydantic import BaseModel

class ChatRequest(BaseModel):
    """聊天请求模型"""
    question: str
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    """聊天响应模型"""
    sql: str
    data: list
    summary: str
    chart_type: str = "table"  # table, line, bar, pie
    execution_time: Optional[float] = None

class ChatHistory(BaseModel):
    """聊天历史模型"""
    id: str
    question: str
    response: ChatResponse
    timestamp: str
