# 前端文档

## 概述

基于 Vue 3 + TypeScript 的现代化前端应用，为进销存 BI 系统提供优秀的用户体验。

## 核心特性

- **现代化框架**: Vue 3 Composition API + TypeScript
- **UI 组件**: Element Plus + 自定义设计系统
- **图表可视化**: ECharts 5 支持丰富的图表类型
- **状态管理**: Pinia 提供可预测的状态管理
- **样式系统**: Tailwind CSS + 暗色主题支持
- **类型安全**: 完整的 TypeScript 类型定义

## 技术架构

### 页面结构 (views/)
- `Login/`: 用户登录页面
- `Dashboard/`: 经营驾驶舱 - KPI 指标展示
- `Analysis/`: 智能分析 - AI 问答界面
- `Reports/`: 报表中心 - 数据导出和管理
- `Operations/`: 业务操作 - 日常业务处理
- `Settings/`: 系统设置 - 用户配置管理

### 组件系统 (components/)
- `Charts/`: ECharts 图表组件封装
- `Layout/`: 应用布局组件

### 状态管理 (stores/)
- `user.ts`: 用户状态和权限管理

### API 集成 (api/)
- `auth.ts`: 认证相关接口
- `business.ts`: 业务数据接口
- `dashboard.ts`: 仪表板数据接口

## 开发指南

### 环境配置
```bash
cd frontend
npm install
```

### 运行开发服务器
```bash
npm run dev
```

### 构建生产版本
```bash
npm run build
```

## 设计规范

### 主题系统
- 支持浅色/暗色主题切换
- 默认暗色主题，优化 BI 数据展示体验
- 统一的颜色系统和组件样式

### 交互设计
- 遵循 BI 系统交互最佳实践
- 响应式设计，支持多种屏幕尺寸
- 无障碍访问支持

## 图表组件

### BaseChart.vue
通用图表组件，支持：
- 折线图、柱状图、饼图、散点图等
- 自定义配置和主题适配
- 响应式布局和数据更新
- 交互事件处理
