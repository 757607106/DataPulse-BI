# 后端文档

## 概述

基于 FastAPI 的现代化异步 Web API 服务，为进销存 BI 系统提供强大的后端支持。

## 核心特性

- **异步处理**: 所有 API 端点使用 async/await 模式
- **类型安全**: 完整的 Pydantic 数据验证
- **AI 集成**: Vanna.ai 提供自然语言转 SQL 能力
- **高性能**: SQLAlchemy 2.0 + PostgreSQL + Redis 缓存
- **可扩展**: 模块化架构，易于维护和扩展

## 技术架构

### API 层 (api/v1/endpoints/)
- `auth.py`: 用户认证和权限管理
- `business.py`: 业务数据操作
- `chat.py`: AI 智能问答
- `dashboard.py`: 仪表板数据服务
- `report.py`: 报表生成和导出

### 服务层 (services/)
- `vanna_service.py`: Vanna AI 核心服务

### 数据层
- `models/`: SQLAlchemy ORM 模型
- `schemas/`: Pydantic 数据验证模型
- `db/`: 数据库会话和初始化

## 开发指南

### 环境配置
```bash
cd backend
pip install -r requirements.txt
```

### 运行服务
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### API 文档
启动服务后访问: http://localhost:8000/docs
