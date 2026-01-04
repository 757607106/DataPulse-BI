# Dashboard 页面使用指南

## 概述

基于 React Figma 设计稿重构的 Vue 3 Dashboard 页面，集成了 KPI 卡片、ECharts 图表和 Element Plus 表格组件。

## 文件结构

```
src/views/Dashboard/
├── index.vue              # 主页面
├── components/
│   └── KPICard.vue        # KPI 卡片组件
└── README.md             # 使用说明
```

## 功能特性

### ✅ 已实现功能

1. **KPI 卡片展示**
   - 4个核心指标：销售额、订单数、客单价、库存周转率
   - 趋势指示器（上升/下降）
   - 小型趋势图 (Sparkline)
   - 悬停发光效果

2. **图表展示**
   - 销售趋势分析（折线图）：销售额、成本、利润
   - 产品销售占比（饼图）：各产品类别占比
   - 基于 BaseChart 组件，支持深色模式

3. **库存预警表格**
   - Element Plus 表格组件
   - 搜索功能
   - 批量操作（删除）
   - 导出功能（预留）
   - 分页组件
   - 响应式设计

### 🎨 视觉设计

- **深色主题**：完全适配 Dark Mode Only 设计
- **渐变背景**：使用 Tailwind CSS 实现玻璃态效果
- **悬停动画**：卡片和按钮的交互反馈
- **响应式布局**：支持移动端适配

## 使用方法

### 1. 路由配置

在 `src/router/modules/` 中添加路由配置：

```typescript
// dashboard.ts
export default {
  path: '/dashboard',
  name: 'Dashboard',
  component: () => import('@/views/Dashboard/index.vue'),
  meta: {
    title: '经营驾驶舱',
    icon: 'dashboard',
    roles: ['admin', 'manager']
  }
}
```

### 2. 权限配置

确保在路由守卫中配置相应的权限检查。

### 3. 数据集成

#### Mock 数据替换

当前使用的是静态 Mock 数据，需要替换为真实的 API 调用：

```typescript
// 在 index.vue 中替换 mockData
import { useDashboardStore } from '@/stores/dashboard'

const dashboardStore = useDashboardStore()

// 获取实时数据
onMounted(async () => {
  await dashboardStore.fetchKPIData()
  await dashboardStore.fetchChartData()
  await dashboardStore.fetchInventoryData()
})
```

#### API 接口定义

```typescript
// src/api/dashboard.ts
export const dashboardApi = {
  // 获取 KPI 数据
  getKPIData: () => request.get('/api/v1/dashboard/kpis'),

  // 获取图表数据
  getChartData: (params: any) => request.get('/api/v1/dashboard/charts', { params }),

  // 获取库存数据
  getInventoryData: (params: any) => request.get('/api/v1/dashboard/inventory', { params }),

  // 导出库存数据
  exportInventory: (params: any) => request.post('/api/v1/dashboard/inventory/export', params, {
    responseType: 'blob'
  })
}
```

### 4. 状态管理

创建 Pinia store 管理 Dashboard 状态：

```typescript
// src/stores/dashboard.ts
export const useDashboardStore = defineStore('dashboard', () => {
  const kpiData = ref([])
  const chartData = ref({})
  const inventoryData = ref([])
  const loading = ref(false)

  const fetchKPIData = async () => {
    loading.value = true
    try {
      const res = await dashboardApi.getKPIData()
      kpiData.value = res.data
    } finally {
      loading.value = false
    }
  }

  const fetchChartData = async (dateRange: string) => {
    const res = await dashboardApi.getChartData({ dateRange })
    chartData.value = res.data
  }

  const fetchInventoryData = async () => {
    const res = await dashboardApi.getInventoryData()
    inventoryData.value = res.data
  }

  return {
    kpiData,
    chartData,
    inventoryData,
    loading,
    fetchKPIData,
    fetchChartData,
    fetchInventoryData
  }
})
```

## 组件说明

### KPICard 组件

专用的 KPI 指标卡片组件，包含：

- **Props**:
  - `title`: 指标名称
  - `value`: 指标数值
  - `change`: 变化百分比
  - `trend`: 趋势方向 ('up' | 'down')
  - `sparklineData`: 趋势图数据数组
  - `accentColor`: 主题色

- **Events**:
  - `click`: 点击事件，传递指标信息

### BaseChart 组件

复用的 ECharts 封装组件，支持：

- 自动响应式
- 深色模式切换
- 事件绑定
- 加载状态

## 样式定制

### 主题色配置

在 `tailwind.config.js` 中配置自定义颜色：

```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        'brand-cyan': '#06B6D4',
        'brand-green': '#10B981',
        'brand-yellow': '#F59E0B',
        'brand-red': '#EF4444'
      }
    }
  }
}
```

### 全局样式

在 `src/style/index.scss` 中添加全局样式：

```scss
// 深色模式变量
:root {
  --bg-primary: #0f172a;
  --bg-secondary: #1e293b;
  --text-primary: #ffffff;
  --text-secondary: #94a3b8;
  --border-color: #334155;
}

// 卡片悬停效果
.card-hover {
  @apply transition-all duration-300 ease-in-out;
  &:hover {
    @apply transform -translate-y-1 shadow-xl;
  }
}
```

## 扩展功能

### 1. 时间筛选器

添加日期范围选择器：

```vue
<template>
  <el-date-picker
    v-model="dateRange"
    type="daterange"
    range-separator="至"
    start-placeholder="开始日期"
    end-placeholder="结束日期"
    @change="handleDateChange"
  />
</template>
```

### 2. 图表交互

添加图表联动功能：

```typescript
const handleChartClick = (params: any) => {
  // 图表点击联动逻辑
  // 更新其他图表或表格筛选条件
}
```

### 3. 实时更新

添加 WebSocket 实时数据更新：

```typescript
import { io } from 'socket.io-client'

const socket = io('ws://localhost:8000')

socket.on('dashboard-update', (data) => {
  // 更新 Dashboard 数据
  updateDashboardData(data)
})
```

## 性能优化

1. **懒加载**: 对大型图表组件使用动态导入
2. **缓存**: 对频繁查询的数据使用内存缓存
3. **防抖**: 对搜索输入使用防抖处理
4. **虚拟滚动**: 对大数据表格使用虚拟滚动

## 浏览器兼容性

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 故障排除

### 常见问题

1. **图表不显示**: 检查 ECharts 是否正确安装
2. **样式错乱**: 确认 Tailwind CSS 配置正确
3. **数据不更新**: 检查 API 接口和错误处理

### 调试方法

```typescript
// 开启开发模式调试
if (import.meta.env.DEV) {
  console.log('Dashboard data:', dashboardData)
  console.log('Chart options:', chartOptions)
}
```

## 更新日志

- **v1.0.0**: 初始版本，实现基础 Dashboard 功能
- 支持 KPI 卡片展示
- 支持图表可视化
- 支持库存管理表格
