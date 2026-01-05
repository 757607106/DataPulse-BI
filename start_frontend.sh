#!/bin/bash

# 前端启动脚本

echo "=================================="
echo "进销存 BI 前端 - 启动脚本"
echo "=================================="

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装"
    exit 1
fi

# 1. 安装依赖
echo ""
echo "📦 安装前端依赖..."
cd frontend
npm install

# 2. 启动前端
echo ""
echo "🚀 启动前端开发服务器..."
echo "访问: http://localhost:5173"
npm run dev
