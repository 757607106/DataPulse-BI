// ECharts 相关类型定义
export type { EChartsOption } from 'echarts'

// 自定义图表主题类型
export type ChartTheme = 'light' | 'dark' | 'auto'

// 图表类型
export type ChartType = 'line' | 'bar' | 'pie' | 'scatter' | 'radar' | 'heatmap' | 'tree' | 'treemap' | 'sunburst' | 'funnel' | 'gauge'

// 基础图表配置接口
export interface BaseChartProps {
  option: EChartsOption
  width?: string | number
  height?: string | number
  theme?: ChartTheme
  notMerge?: boolean
  lazyUpdate?: boolean
  silent?: boolean
}

// 图表数据接口
export interface ChartDataItem {
  name: string
  value: number | string
  [key: string]: any
}

// 系列数据接口
export interface SeriesItem {
  name?: string
  type?: ChartType
  data: ChartDataItem[] | number[]
  [key: string]: any
}

// 坐标轴配置
export interface AxisConfig {
  type?: 'category' | 'value' | 'time' | 'log'
  data?: string[] | number[]
  name?: string
  [key: string]: any
}

// 提示框配置
export interface TooltipConfig {
  trigger?: 'item' | 'axis' | 'none'
  formatter?: string | Function
  [key: string]: any
}

// 图例配置
export interface LegendConfig {
  show?: boolean
  data?: string[]
  orient?: 'horizontal' | 'vertical'
  [key: string]: any
}

// 网格配置
export interface GridConfig {
  left?: string | number
  right?: string | number
  top?: string | number
  bottom?: string | number
  containLabel?: boolean
}

// 标题配置
export interface TitleConfig {
  text?: string
  subtext?: string
  left?: string | number
  top?: string | number
  textStyle?: {
    color?: string
    fontSize?: number
    fontWeight?: string | number
    [key: string]: any
  }
}

// 常用图表配置预设
export interface LineChartOption extends EChartsOption {
  title?: TitleConfig
  tooltip?: TooltipConfig
  legend?: LegendConfig
  grid?: GridConfig
  xAxis?: AxisConfig | AxisConfig[]
  yAxis?: AxisConfig | AxisConfig[]
  series?: SeriesItem[]
}

// 图表事件接口
export interface ChartEvents {
  ready: [instance: any]
  click: [params: any]
  mouseover: [params: any]
  mouseout: [params: any]
}

// 暴露的实例方法接口
export interface ChartExposed {
  getChart: () => any
  resize: () => void
  setOption: (option: any, opts?: any) => void
  clear: () => void
  showLoading: (text?: string) => void
  hideLoading: () => void
}

export interface BarChartOption extends EChartsOption {
  title?: TitleConfig
  tooltip?: TooltipConfig
  legend?: LegendConfig
  grid?: GridConfig
  xAxis?: AxisConfig | AxisConfig[]
  yAxis?: AxisConfig | AxisConfig[]
  series?: SeriesItem[]
}

export interface PieChartOption extends EChartsOption {
  title?: TitleConfig
  tooltip?: TooltipConfig
  legend?: LegendConfig
  series?: Array<{
    name?: string
    type: 'pie'
    radius?: string | number | [number, number] | [string, string]
    center?: [string | number, string | number]
    data: ChartDataItem[]
    [key: string]: any
  }>
}

// 事件参数类型
export interface ChartEventParams {
  componentType: string
  seriesType: string
  seriesIndex: number
  seriesName: string
  name: string
  dataIndex: number
  data: any
  value: any
  color: string
  [key: string]: any
}

// 组件事件定义
export interface ChartEvents {
  ready: [chart: any]
  click: [params: ChartEventParams]
  mouseover: [params: ChartEventParams]
  mouseout: [params: ChartEventParams]
}

// 暴露的方法
export interface ChartExposed {
  getChart: () => any
  resize: () => void
  setOption: (option: EChartsOption, opts?: any) => void
  clear: () => void
  showLoading: (text?: string) => void
  hideLoading: () => void
}
