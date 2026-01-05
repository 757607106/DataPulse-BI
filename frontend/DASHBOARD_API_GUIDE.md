# Dashboard API 对接使用指南

## 🎯 实现概述

前端 Dashboard 页面已成功对接后端真实 API，支持：
- 自动加载数据
- JWT 认证
- Loading 状态
- 错误处理和重试
- 降级到 Mock 数据

## 📁 新增文件

### 1. 类型定义
```
frontend/src/types/dashboard.ts
```
定义了所有 API 响应数据的 TypeScript 接口

### 2. HTTP 封装
```
frontend/src/utils/http.ts
```
- 自动添加 JWT Token (从 `localStorage.access_token`)
- 拦截 401 错误并清除 Token
- 统一错误处理

### 3. API 接口
```
frontend/src/api/dashboard.ts
```
- `getDashboardData()`: 获取完整仪表盘数据
- `getKPIData()`: 获取 KPI 数据

### 4. 环境变量
```
frontend/.env
frontend/.env.development
frontend/.env.production
```
配置 API 基础 URL

## 🚀 使用步骤

### 1. 启动后端
```bash
cd backend
uvicorn app.main:app --reload
```
后端将运行在 `http://localhost:8000`

### 2. 启动前端
```bash
cd frontend
npm run dev
```
前端将运行在 `http://localhost:5173` (或其他端口)

### 3. 登录获取 Token

#### 方式 1: 使用 API 登录
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'
```

响应示例:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### 方式 2: 在浏览器控制台手动设置 (测试用)
```javascript
localStorage.setItem('access_token', 'your_jwt_token_here');
```

### 4. 访问 Dashboard
打开 `http://localhost:5173` (或前端运行的地址)，导航到 Dashboard 页面。

页面将自动：
1. 从 localStorage 读取 Token
2. 调用 `/api/v1/dashboard/overview` 接口
3. 显示 Loading 状态
4. 加载成功后渲染真实数据
5. 加载失败则显示错误提示或降级到 Mock 数据

## 🎨 数据流

```
用户访问页面
    ↓
onMounted() 生命周期
    ↓
loadDashboardData()
    ↓
getDashboardData() (带 JWT Token)
    ↓
HTTP 请求 → Backend API
    ↓
响应数据 → dashboardData ref
    ↓
computed 计算属性 (kpiData, salesData, inventoryData)
    ↓
Template 模板绑定
    ↓
BaseChart 组件渲染 ECharts
```

## 📊 数据绑定

### KPI 卡片
```typescript
// API 数据 → KPI 卡片
kpiData = {
  sales: { value: kpi.total_sales, ... },
  purchase: { value: total_sales - gross_profit, ... },
  inventory: { value: receivable + payable, ... },
  alerts: { value: inventory_alerts.length, ... }
}
```

### 趋势图
```typescript
// API trends → ECharts 折线图
salesData = trends.map(t => ({
  month: t.date.substring(5),  // MM-DD
  sales: t.sales,
  cost: t.sales - t.profit,
  profit: t.profit
}))
```

### 库存预警
```typescript
// API inventory_alerts → 表格数据
inventoryData = inventory_alerts.map(alert => ({
  product: alert.product_name,
  stock: alert.current_stock,
  safeStock: alert.min_stock,
  status: alert.stock_status,
  ...
}))
```

## 🔐 认证机制

### Token 存储
```javascript
// 登录后存储 Token
localStorage.setItem('access_token', token);

// 请求拦截器自动添加
config.headers.Authorization = `Bearer ${token}`;
```

### 401 处理
```javascript
// 响应拦截器自动处理 401
if (error.response?.status === 401) {
  localStorage.removeItem('access_token');
  // 跳转到登录页 (可选)
}
```

## 🛠️ 调试技巧

### 1. 查看 API 请求
打开浏览器开发者工具 → Network 标签，筛选 XHR 请求

### 2. 查看 Console 日志
```javascript
// 查看数据加载日志
console.log('Dashboard data:', dashboardData.value);
console.log('KPI:', kpiData.value);
console.log('Trends:', salesData.value);
```

### 3. 检查 Token
```javascript
// 控制台查看当前 Token
console.log('Token:', localStorage.getItem('access_token'));
```

### 4. 手动刷新数据
```javascript
// 页面中点击刷新按钮，或在控制台手动调用
await loadDashboardData();
```

## ⚠️ 常见问题

### Q1: 显示"未授权，请先登录"
**原因**: localStorage 中没有 Token 或 Token 过期
**解决**: 重新登录获取新 Token

### Q2: 显示"数据加载失败"
**原因**: 
- 后端未启动
- API URL 配置错误
- 网络问题

**解决**: 
1. 确认后端运行正常
2. 检查 `.env` 文件中的 `VITE_API_BASE_URL`
3. 查看 Network 标签的错误详情

### Q3: 数据不更新
**原因**: 
- computed 属性缓存
- 响应式数据未正确更新

**解决**: 
1. 点击刷新按钮
2. 重新加载页面

## 📝 环境变量说明

```env
# .env
VITE_API_BASE_URL=http://localhost:8000

# .env.development (开发环境)
VITE_API_BASE_URL=http://localhost:8000

# .env.production (生产环境)
VITE_API_BASE_URL=https://api.your-domain.com
```

Vite 会根据运行命令自动选择配置：
- `npm run dev` → .env.development
- `npm run build` → .env.production

## 🎉 完成！

前端 Dashboard 已成功对接后端 API，现在可以：
- ✅ 自动加载真实数据
- ✅ JWT 认证保护
- ✅ Loading 和 Error 状态
- ✅ 图表自动更新
- ✅ 降级到 Mock 数据（开发/演示用）
