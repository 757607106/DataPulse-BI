"""
核心配置文件
"""
import os
from typing import Optional
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings

class Settings(BaseSettings):
    """应用配置"""

    # 数据库配置
    database_url: str = "postgresql+asyncpg://postgres:postgres123@localhost:5432/inventory_bi"
    # 同步数据库连接（用于初始化和迁移）
    database_url_sync: str = "postgresql+psycopg2://postgres:postgres123@localhost:5432/inventory_bi"

    # Redis 配置
    redis_url: str = "redis://localhost:6379/0"

    # AI 服务配置
    dashscope_api_key: str = ""

    # 应用配置
    app_name: str = "进销存 BI 系统"
    app_version: str = "1.0.0"
    debug: bool = True

    # 安全配置
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = False

# 创建全局配置实例
settings = Settings()

# 从环境变量读取敏感信息
if os.getenv("DASHSCOPE_API_KEY"):
    settings.dashscope_api_key = os.getenv("DASHSCOPE_API_KEY")

if os.getenv("DATABASE_URL"):
    settings.database_url = os.getenv("DATABASE_URL")

if os.getenv("REDIS_URL"):
    settings.redis_url = os.getenv("REDIS_URL")
