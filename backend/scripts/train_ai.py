"""
Vanna AI 训练脚本

用途：初始化 Vanna AI 系统，训练 DDL 和问答对

运行方式：
    python -m scripts.train_ai
    
或使用异步运行：
    python scripts/train_ai.py
"""
import sys
import os
import asyncio

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from loguru import logger
from app.services.vanna_service import vanna_service
from app.core.config import settings


async def main():
    """主函数"""
    logger.info("=" * 80)
    logger.info("🚀 Vanna AI 训练脚本启动")
    logger.info("=" * 80)
    
    # 检查必要的环境变量
    if not settings.dashscope_api_key:
        logger.error("❌ 错误: 未配置 DASHSCOPE_API_KEY 环境变量")
        logger.error("   请在 .env 文件或环境变量中设置 DASHSCOPE_API_KEY")
        sys.exit(1)
    
    logger.info(f"✅ 配置检查通过")
    logger.info(f"   - 数据库: {settings.database_url_sync}")
    logger.info(f"   - Redis: {settings.redis_url}")
    logger.info(f"   - API Key: {settings.dashscope_api_key[:10]}***")
    logger.info("")
    
    try:
        # 执行训练
        await vanna_service.train_system()
        
        logger.info("")
        logger.info("=" * 80)
        logger.info("🎉 训练完成！Vanna AI 已准备就绪")
        logger.info("=" * 80)
        logger.info("")
        logger.info("下一步：")
        logger.info("  1. 启动后端服务: uvicorn app.main:app --reload")
        logger.info("  2. 测试 Chat 接口: POST /api/v1/chat")
        logger.info("")
        
    except Exception as e:
        logger.error(f"❌ 训练失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        # 关闭连接
        await vanna_service.close()


if __name__ == "__main__":
    # Python 3.7+ 推荐写法
    asyncio.run(main())
