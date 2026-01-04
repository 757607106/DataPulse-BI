# 进销存智能 BI 系统 - 技术栈架构文档

## 1. 总体架构
* **前端基础**: 基于 **Vue Pure Admin** (非精简版) 进行二次开发。
* **后端服务**: Python FastAPI + AI (Vanna) + PostgreSQL (pgvector)。

## 2. 前端技术栈 (Frontend - Vue Pure Admin)
* **核心框架**: Vue 3 (Script Setup)
* **脚手架**: Vite 4+
* **基础模版**: **Vue Pure Admin** (GitHub Star 15k+)
* **UI 组件库**: Element Plus (模版内置)
* **CSS 框架**: **Tailwind CSS** (模版内置，推荐用于布局和微调)
* **图表库**: ECharts 5 (需封装为组件)
* **图标库**: Iconify (模版内置)
* **网络请求**: Axios (使用模版封装好的 `pure-admin-utils` 或自定义封装)

## 3. 后端技术栈 (Backend)
* **语言**: Python 3.10+
* **Web 框架**: FastAPI
* **AI 核心**: Vanna.ai + 阿里百炼 (Qwen)
* **数据库**: PostgreSQL 16 + pgvector (Docker 部署，适配 ARM64)
* **缓存**: Redis (Docker 部署)
* **ORM**: SQLAlchemy (Async)

### 3.1 安全配置
* **API Key**: `DASHSCOPE_API_KEY` 必须从环境变量 (`os.getenv`) 读取。
* **数据库密码**: 禁止硬编码，使用 `.env` 文件管理。

## 4. 基础设施 (Docker for MacOS M4)
* **数据库镜像**: `pgvector/pgvector:pg16` (支持 Linux/ARM64)
* **缓存镜像**: `redis:alpine`

## 5. 开发规范
* **目录结构**: 严格遵循 Vue Pure Admin 的目录规范：
    * `src/views/`: 页面文件
    * `src/router/modules/`: 路由配置 (动态路由)
    * `src/api/`: 接口定义
* **代码风格**: 优先使用 Tailwind 类名，减少手写 `<style scoped>`.