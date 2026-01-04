<template>
  <div
    class="kpi-card relative overflow-hidden rounded-xl bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-slate-700/50 p-6 hover:border-cyan-400 hover:shadow-lg transition-all cursor-pointer group"
    @click="handleClick"
  >
    <!-- Neon Glow Effect -->
    <div
      class="absolute top-0 right-0 w-32 h-32 rounded-full blur-3xl opacity-20"
      :style="{ backgroundColor: accentColor }"
    ></div>

    <!-- Content -->
    <div class="relative">
      <div class="flex items-start justify-between mb-4">
        <div>
          <p class="text-sm font-medium text-slate-400 mb-1">{{ title }}</p>
          <h3 class="text-2xl font-bold tracking-tight text-white">{{ value }}</h3>
        </div>
        <div
          class="w-10 h-10 rounded-lg flex items-center justify-center"
          :style="{ backgroundColor: `${accentColor}20` }"
        >
          <el-icon
            :class="{ 'text-green-400': trend === 'up', 'text-red-400': trend === 'down' }"
            size="20"
          >
            <ArrowUp v-if="trend === 'up'" />
            <ArrowDown v-else />
          </el-icon>
        </div>
      </div>

      <!-- Sparkline -->
      <div class="mb-3 -mx-2">
        <BaseChart :option="sparklineOption" height="40px" />
      </div>

      <!-- Change Indicator -->
      <div class="flex items-center gap-2">
        <span
          class="text-sm font-semibold"
          :style="{ color: trend === 'up' ? '#10B981' : '#EF4444' }"
        >
          {{ change }}
        </span>
        <span class="text-xs font-medium text-slate-500">较上期</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ArrowUp, ArrowDown } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import BaseChart from '@/components/Charts/BaseChart.vue'

// 定义组件选项
defineOptions({
  name: 'KPICard'
})

// Props 定义
interface Props {
  title: string
  value: string
  change: string
  trend: 'up' | 'down'
  sparklineData: number[]
  accentColor: string
}

const props = defineProps<Props>()

// Emits 定义
const emit = defineEmits<{
  click: [title: string, value: string, change: string]
}>()

// Sparkline 图表配置
const sparklineOption = computed(() => ({
  grid: {
    left: 0,
    right: 0,
    top: 0,
    bottom: 0,
    containLabel: false
  },
  xAxis: {
    type: 'category',
    show: false,
    data: props.sparklineData.map((_, index) => index.toString())
  },
  yAxis: {
    type: 'value',
    show: false
  },
  series: [{
    type: 'line',
    data: props.sparklineData,
    smooth: true,
    symbol: 'none',
    lineStyle: {
      color: props.accentColor,
      width: 2
    },
    areaStyle: {
      color: {
        type: 'linear',
        x: 0, y: 0, x2: 0, y2: 1,
        colorStops: [
          { offset: 0, color: `${props.accentColor}40` },
          { offset: 1, color: `${props.accentColor}10` }
        ]
      }
    }
  }],
  tooltip: {
    show: false
  }
}))

// 事件处理
const handleClick = () => {
  ElMessage.info(`查看${props.title}详情\n当前值: ${props.value}\n变化: ${props.change}`)
  emit('click', props.title, props.value, props.change)
}
</script>

<style scoped>
.kpi-card {
  transition: all 0.3s ease;
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .kpi-card {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.5) 0%, rgba(15, 23, 42, 0.5) 100%);
  }
}
</style>
