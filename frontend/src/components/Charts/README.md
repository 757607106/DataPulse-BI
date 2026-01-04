# ECharts 组件使用指南

## BaseChart.vue - 通用 ECharts 封装组件

### 功能特性

- ✅ 支持 Vue 3 Composition API
- ✅ 原生 ECharts 集成，无额外依赖
- ✅ 自动响应式布局 (ResizeObserver + window resize)
- ✅ 智能深色模式支持 (跟随系统主题或手动设置)
- ✅ 完整的事件绑定 (click, mouseover, mouseout)
- ✅ TypeScript 支持
- ✅ 内存安全 (自动清理资源)

### 基本用法

```vue
<template>
  <div class="chart-container">
    <BaseChart
      :option="chartOption"
      width="100%"
      height="400px"
      theme="auto"
      @ready="onChartReady"
      @click="onChartClick"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import BaseChart from '@/components/Charts/BaseChart.vue'
import type { EChartsOption } from 'echarts'

// 图表配置
const chartOption = reactive<EChartsOption>({
  title: {
    text: '销售数据统计'
  },
  tooltip: {
    trigger: 'axis'
  },
  xAxis: {
    type: 'category',
    data: ['1月', '2月', '3月', '4月', '5月', '6月']
  },
  yAxis: {
    type: 'value'
  },
  series: [{
    name: '销售额',
    type: 'line',
    data: [120, 200, 150, 80, 70, 110]
  }]
})

// 图表就绪回调
const onChartReady = (chart: any) => {
  console.log('图表初始化完成', chart)
}

// 图表点击事件
const onChartClick = (params: any) => {
  console.log('图表点击', params)
}
</script>

<style scoped>
.chart-container {
  width: 100%;
  height: 400px;
}
</style>
```

### Props 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `option` | `EChartsOption` | - | ECharts 配置对象 (必需) |
| `width` | `string \| number` | `'100%'` | 图表宽度 |
| `height` | `string \| number` | `'100%'` | 图表高度 |
| `theme` | `'light' \| 'dark' \| 'auto'` | `'auto'` | 主题模式 |
| `notMerge` | `boolean` | `false` | 是否不跟之前设置的option进行合并 |
| `lazyUpdate` | `boolean` | `false` | 是否延迟更新 |
| `silent` | `boolean` | `false` | 是否静默更新 |

### Events 事件

| 事件名 | 参数 | 说明 |
|--------|------|------|
| `ready` | `chart: ECharts` | 图表初始化完成 |
| `click` | `params: any` | 图表点击事件 |
| `mouseover` | `params: any` | 鼠标悬停事件 |
| `mouseout` | `params: any` | 鼠标离开事件 |

### 暴露的方法

通过 `ref` 可以访问以下方法：

```vue
<template>
  <BaseChart ref="chartRef" :option="option" />
</template>

<script setup>
const chartRef = ref()

// 获取图表实例
const chart = chartRef.value?.getChart()

// 手动调整大小
chartRef.value?.resize()

// 更新配置
chartRef.value?.setOption(newOption)

// 清空图表
chartRef.value?.clear()

// 显示加载状态
chartRef.value?.showLoading('数据加载中...')

// 隐藏加载状态
chartRef.value?.hideLoading()
</script>
```

### 深色模式支持

组件自动支持深色模式：

1. **自动模式** (`theme="auto"`)：跟随系统主题
2. **手动模式** (`theme="dark"` 或 `theme="light"`)：固定主题

```vue
<!-- 跟随系统主题 -->
<BaseChart :option="option" theme="auto" />

<!-- 强制深色模式 -->
<BaseChart :option="option" theme="dark" />

<!-- 强制浅色模式 -->
<BaseChart :option="option" theme="light" />
```

### 与 Pinia 集成

可以与状态管理器结合使用：

```vue
<script setup>
import { storeToRefs } from 'pinia'
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()
const { isDark } = storeToRefs(themeStore)

// 使用 store 的主题状态
<BaseChart
  :option="chartOption"
  :theme="isDark ? 'dark' : 'light'"
/>
</script>
```

### 响应式布局

组件内置响应式支持：

- 使用 `ResizeObserver` 监听容器大小变化
- 自动调用 `chart.resize()`
- 支持窗口大小变化
- 防抖处理，避免频繁调用

### 注意事项

1. **内存管理**：组件会在卸载时自动清理 ECharts 实例和事件监听器
2. **主题切换**：当主题改变时会重新初始化图表，可能会有短暂的闪烁
3. **性能优化**：大量数据时建议使用 `lazyUpdate` 和适当的防抖
4. **TypeScript**：建议使用 `EChartsOption` 类型定义配置对象

### 常见图表类型

#### 柱状图

```javascript
const barOption = {
  title: { text: '月度销售对比' },
  tooltip: { trigger: 'axis' },
  xAxis: {
    type: 'category',
    data: ['1月', '2月', '3月', '4月', '5月', '6月']
  },
  yAxis: { type: 'value' },
  series: [{
    name: '销售额',
    type: 'bar',
    data: [12000, 15000, 18000, 14000, 16000, 20000]
  }]
}
```

#### 饼图

```javascript
const pieOption = {
  title: { text: '产品占比' },
  tooltip: { trigger: 'item' },
  series: [{
    name: '占比',
    type: 'pie',
    radius: '50%',
    data: [
      { value: 35, name: '产品A' },
      { value: 30, name: '产品B' },
      { value: 25, name: '产品C' },
      { value: 10, name: '其他' }
    ]
  }]
}
```

#### 折线图

```javascript
const lineOption = {
  title: { text: '趋势分析' },
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'] },
  yAxis: { type: 'value' },
  series: [{
    name: '访问量',
    type: 'line',
    smooth: true,
    data: [820, 932, 901, 934, 1290, 1330, 1320]
  }]
}
```
