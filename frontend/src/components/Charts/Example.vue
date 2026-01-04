<template>
  <div class="example-container">
    <h2>ECharts 组件使用示例</h2>

    <!-- 基础示例 -->
    <div class="chart-section">
      <h3>基础折线图</h3>
      <BaseChart
        :option="lineOption"
        height="300px"
        @click="handleChartClick"
      />
    </div>

    <!-- 深色模式示例 -->
    <div class="chart-section">
      <h3>深色模式饼图</h3>
      <BaseChart
        :option="pieOption"
        height="300px"
        theme="dark"
      />
    </div>

    <!-- 响应式示例 -->
    <div class="chart-section">
      <h3>响应式柱状图</h3>
      <BaseChart
        ref="barChartRef"
        :option="barOption"
        height="300px"
        @ready="handleChartReady"
      />
    </div>

    <!-- 控制按钮 -->
    <div class="controls">
      <button @click="updateData">更新数据</button>
      <button @click="toggleLoading">切换加载状态</button>
      <button @click="resizeChart">调整大小</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import BaseChart from './BaseChart.vue'
import type { LineChartOption, PieChartOption, BarChartOption } from '@/types/echarts'

// 图表引用
const barChartRef = ref()

// 折线图配置
const lineOption = reactive<LineChartOption>({
  title: {
    text: '月度销售趋势',
    left: 'center'
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
    smooth: true,
    data: [12000, 15000, 18000, 14000, 16000, 20000],
    itemStyle: {
      color: '#409EFF'
    }
  }]
})

// 饼图配置
const pieOption = reactive<PieChartOption>({
  title: {
    text: '产品销售占比',
    left: 'center'
  },
  tooltip: {
    trigger: 'item',
    formatter: '{a} <br/>{b}: {c} ({d}%)'
  },
  legend: {
    orient: 'vertical',
    left: 'left'
  },
  series: [{
    name: '销售占比',
    type: 'pie',
    radius: ['40%', '70%'],
    center: ['60%', '50%'],
    data: [
      { value: 35, name: '产品A' },
      { value: 30, name: '产品B' },
      { value: 25, name: '产品C' },
      { value: 10, name: '其他' }
    ]
  }]
})

// 柱状图配置
const barOption = reactive<BarChartOption>({
  title: {
    text: '季度对比',
    left: 'center'
  },
  tooltip: {
    trigger: 'axis'
  },
  xAxis: {
    type: 'category',
    data: ['Q1', 'Q2', 'Q3', 'Q4']
  },
  yAxis: {
    type: 'value'
  },
  series: [{
    name: '本年',
    type: 'bar',
    data: [12000, 15000, 18000, 14000],
    itemStyle: {
      color: '#67C23A'
    }
  }, {
    name: '去年',
    type: 'bar',
    data: [10000, 13000, 16000, 12000],
    itemStyle: {
      color: '#E6A23C'
    }
  }]
})

// 事件处理
const handleChartClick = (params: any) => {
  console.log('图表点击:', params)
  alert(`点击了: ${params.name} - 值: ${params.value}`)
}

const handleChartReady = (chart: any) => {
  console.log('柱状图初始化完成:', chart)
}

// 控制方法
const updateData = () => {
  // 更新折线图数据
  lineOption.series[0].data = [
    Math.random() * 20000,
    Math.random() * 20000,
    Math.random() * 20000,
    Math.random() * 20000,
    Math.random() * 20000,
    Math.random() * 20000
  ]
}

const toggleLoading = () => {
  if (barChartRef.value) {
    const isLoading = Math.random() > 0.5
    if (isLoading) {
      barChartRef.value.showLoading('数据加载中...')
      setTimeout(() => {
        barChartRef.value?.hideLoading()
      }, 2000)
    } else {
      barChartRef.value.hideLoading()
    }
  }
}

const resizeChart = () => {
  if (barChartRef.value) {
    barChartRef.value.resize()
  }
}
</script>

<style scoped>
.example-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.chart-section {
  margin-bottom: 40px;
  padding: 20px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background: #fafafa;
}

.chart-section h3 {
  margin-bottom: 20px;
  color: #303133;
  font-size: 18px;
}

.controls {
  display: flex;
  gap: 10px;
  margin-top: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.controls button {
  padding: 8px 16px;
  background: #409EFF;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.controls button:hover {
  background: #66b1ff;
}

.controls button:active {
  background: #3a8ee6;
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .chart-section {
    background: #1f1f1f;
    border-color: #333;
  }

  .chart-section h3 {
    color: #e5eaf3;
  }

  .controls {
    background: #141414;
  }
}
</style>
