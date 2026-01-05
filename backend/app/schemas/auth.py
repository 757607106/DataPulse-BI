"""
认证相关的 Pydantic 模型
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Token(BaseModel):
    """访问令牌响应"""
    access_token: str = Field(..., description="JWT 访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")


class TokenData(BaseModel):
    """令牌数据"""
    username: Optional[str] = None
    role: Optional[str] = None


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=50, description="密码")


class UserBase(BaseModel):
    """用户基础信息"""
    username: str = Field(..., description="用户名")
    role: str = Field(..., description="角色")
    is_active: bool = Field(..., description="是否激活")


class UserResponse(UserBase):
    """用户响应"""
    id: int = Field(..., description="用户ID")
    created_at: datetime = Field(..., description="创建时间")
    
    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    """创建用户请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=50, description="密码")
    role: str = Field(default="user", description="角色：admin/user")
