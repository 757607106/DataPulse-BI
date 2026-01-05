#!/bin/bash

# 进销存 BI 系统启动脚本

echo "=================================="
echo "进销存 BI 系统 - 启动脚本"
echo "=================================="

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi

# 检查 PostgreSQL
if ! command -v psql &> /dev/null; then
    echo "⚠️  psql 未找到，请确保 PostgreSQL 已安装"
fi

# 1. 安装 Python 依赖
echo ""
echo "📦 安装 Python 依赖..."
cd backend
pip3 install -r requirements.txt

# 2. 初始化数据库
echo ""
echo "🗄️  初始化数据库..."
python3 -m scripts.init_db

# 3. 启动后端
echo ""
echo "🚀 启动后端服务 (端口 8000)..."
echo "访问: http://localhost:8000/docs"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
