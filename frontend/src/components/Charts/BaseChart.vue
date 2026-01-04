<template>
  <div ref="chartRef" :style="chartStyle" class="base-chart"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick, computed } from 'vue'
import type { BaseChartProps, ChartEvents, ChartExposed } from '@/types/echarts'

// 动态导入ECharts
let echarts: any = null
const loadECharts = async () => {
  if (!echarts) {
    echarts = await import('echarts')
  }
  return echarts
}

// 定义组件选项
defineOptions({
  name: 'BaseChart'
})

// Props 定义（直接使用导入的类型，避免 extends 导致编译器错误）
const props = withDefaults(defineProps<BaseChartProps>(), {
  width: '100%',
  height: '100%',
  theme: 'auto',
  notMerge: false,
  lazyUpdate: false,
  silent: false
})

// Emits 定义
const emit = defineEmits<ChartEvents>()

// 响应式数据
const chartRef = ref<HTMLDivElement>()
let chartInstance: echarts.ECharts | null = null
let resizeObserver: ResizeObserver | null = null

// 计算样式
const chartStyle = computed(() => ({
  width: typeof props.width === 'number' ? `${props.width}px` : props.width,
  height: typeof props.height === 'number' ? `${props.height}px` : props.height
}))

// 获取当前主题
const getCurrentTheme = (): string => {
  if (props.theme !== 'auto') {
    return props.theme
  }

  // 检查系统主题或应用主题
  const isDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
  // 也可以从 Pinia store 获取应用主题设置
  // const themeStore = useThemeStore()
  // return themeStore.isDark ? 'dark' : 'light'

  return isDark ? 'dark' : 'light'
}

// 初始化图表
const initChart = async () => {
  if (!chartRef.value) return

  // 等待ECharts加载
  await loadECharts()

  // 销毁已存在的图表实例
  if (chartInstance) {
    chartInstance.dispose()
  }

  // 获取当前主题
  const theme = getCurrentTheme()

  // 创建图表实例
  chartInstance = echarts.init(chartRef.value, theme)

  // 设置图表配置
  if (props.option) {
    chartInstance.setOption(props.option, {
      notMerge: props.notMerge,
      lazyUpdate: props.lazyUpdate,
      silent: props.silent
    })
  }

  // 绑定事件
  bindEvents()

  // 监听主题变化
  watchThemeChange()

  // 创建 ResizeObserver 监听容器大小变化
  setupResizeObserver()

  // 触发 ready 事件
  emit('ready', chartInstance)
}

// 绑定图表事件
const bindEvents = () => {
  if (!chartInstance) return

  // 点击事件
  chartInstance.on('click', (params: any) => {
    emit('click', params)
  })

  // 鼠标悬停事件
  chartInstance.on('mouseover', (params: any) => {
    emit('mouseover', params)
  })

  // 鼠标离开事件
  chartInstance.on('mouseout', (params: any) => {
    emit('mouseout', params)
  })
}

// 设置 ResizeObserver
const setupResizeObserver = () => {
  if (!chartRef.value) return

  // 清理旧的观察器
  if (resizeObserver) {
    resizeObserver.disconnect()
  }

  // 创建新的观察器
  resizeObserver = new ResizeObserver(() => {
    if (chartInstance) {
      // 延迟执行以避免频繁调用
      setTimeout(() => {
        chartInstance?.resize()
      }, 100)
    }
  })

  // 开始观察
  resizeObserver.observe(chartRef.value)
}

// 监听主题变化
const watchThemeChange = () => {
  // 监听系统主题变化
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
  const handleThemeChange = () => {
    if (props.theme === 'auto' && chartInstance) {
      const newTheme = getCurrentTheme()
      chartInstance.dispose()
      initChart()
    }
  }

  mediaQuery.addEventListener('change', handleThemeChange)

  // 清理函数会在组件卸载时自动调用
  onUnmounted(() => {
    mediaQuery.removeEventListener('change', handleThemeChange)
  })
}

// 监听窗口 resize 事件（备用方案）
const handleWindowResize = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}

// 监听 option 变化
watch(
  () => props.option,
  (newOption) => {
    if (chartInstance && newOption) {
      chartInstance.setOption(newOption, {
        notMerge: props.notMerge,
        lazyUpdate: props.lazyUpdate,
        silent: props.silent
      })
    }
  },
  { deep: true }
)

// 监听主题变化
watch(
  () => props.theme,
  () => {
    if (chartInstance) {
      // 重新初始化图表以应用新主题
      initChart()
    }
  }
)

// 生命周期
onMounted(async () => {
  await nextTick()
  await initChart()

  // 添加窗口 resize 监听器（作为 ResizeObserver 的备用）
  window.addEventListener('resize', handleWindowResize)
})

onUnmounted(() => {
  // 清理资源
  if (resizeObserver) {
    resizeObserver.disconnect()
    resizeObserver = null
  }

  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }

  window.removeEventListener('resize', handleWindowResize)
})

// 暴露方法给父组件
defineExpose({
  getChart: () => chartInstance,
  resize: () => chartInstance?.resize(),
  setOption: (option: any, opts?: any) => chartInstance?.setOption(option, opts),
  clear: () => chartInstance?.clear(),
  showLoading: (text?: string) => chartInstance?.showLoading(text),
  hideLoading: () => chartInstance?.hideLoading()
} as ChartExposed)
</script>

<style scoped>
.base-chart {
  width: 100%;
  height: 100%;
}
</style>
