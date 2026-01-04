<script setup lang="ts">
import { ref, computed } from 'vue';
import { 
  Calendar,
  Download, 
  Refresh, 
  Top,
  Bottom,
  Search,
  Filter,
  Warning,
  Box,
  Edit,
  Delete,
  Plus,
  View,
  ShoppingCart,
  TrophyBase
} from '@element-plus/icons-vue';
import BaseChart from '@/components/Charts/BaseChart.vue';
import type { EChartsOption } from 'echarts';

// --- Types ---
type DateRange = '今日' | '本周' | '本月' | '本季度';
type SortField = 'sales' | 'amount' | 'growth';
type SortOrder = 'asc' | 'desc';

interface InventoryItem {
  id: number;
  product: string;
  sku: string;
  stock: number;
  safeStock: number;
  status: string;
  severity: string;
  value: number;
}

interface TopProduct {
  rank: number;
  name: string;
  sales: number;
  amount: number;
  growth: number;
}

// --- Mock Data Generators (Inline) ---
const generateKPIData = (range: DateRange) => {
  const configs = {
    '今日': {
      sales: { value: 32450, change: 8.5, data: [28, 29, 30, 31, 30, 32, 31, 33, 32, 34, 33, 32] },
      purchase: { value: 21500, change: 6.2, data: [19, 20, 21, 20, 22, 21, 23, 22, 21, 22, 21, 21] },
      inventory: { value: 1245680, change: -0.5, data: [125, 125, 124, 125, 124, 125, 125, 124, 125, 124, 125, 124] },
      alerts: { value: 5, change: 2, data: [3, 3, 4, 3, 4, 3, 4, 4, 5, 4, 5, 5] },
    },
    '本周': {
      sales: { value: 227150, change: 12.3, data: [30, 31, 32, 33, 32, 33, 34] },
      purchase: { value: 150450, change: 9.8, data: [20, 21, 22, 21, 22, 23, 22] },
      inventory: { value: 1245680, change: -1.2, data: [128, 127, 126, 125, 126, 125, 124] },
      alerts: { value: 8, change: 3, data: [5, 6, 7, 6, 7, 8, 8] },
    },
    '本月': {
      sales: { value: 980000, change: 15.8, data: [42, 48, 52, 61, 58, 67, 73, 69, 78, 84, 91, 98] },
      purchase: { value: 650000, change: 12.3, data: [28, 32, 35, 41, 39, 45, 49, 46, 52, 56, 61, 65] },
      inventory: { value: 1245680, change: -3.2, data: [135, 132, 128, 125, 130, 127, 124, 126, 125, 123, 125, 124] },
      alerts: { value: 15, change: 3, data: [8, 9, 10, 11, 12, 10, 13, 12, 14, 13, 12, 15] },
    },
    '本季度': {
      sales: { value: 2940000, change: 18.5, data: [850, 920, 980, 1010, 960, 1020, 1050, 980, 1040, 1100, 1150, 1020] },
      purchase: { value: 1950000, change: 14.7, data: [600, 640, 650, 670, 640, 680, 700, 650, 690, 730, 770, 680] },
      inventory: { value: 1245680, change: -5.8, data: [145, 142, 138, 135, 140, 137, 134, 136, 135, 133, 135, 124] },
      alerts: { value: 23, change: 8, data: [12, 15, 18, 16, 19, 17, 20, 18, 21, 20, 19, 23] },
    },
  };
  return configs[range];
};

const generateMonthlySales = (range: DateRange) => {
  const configs = {
    '今日': [
      { month: '0时', sales: 2800, cost: 1800, profit: 1000 },
      { month: '3时', sales: 1200, cost: 800, profit: 400 },
      { month: '6时', sales: 3500, cost: 2300, profit: 1200 },
      { month: '9时', sales: 5200, cost: 3500, profit: 1700 },
      { month: '12时', sales: 6800, cost: 4500, profit: 2300 },
      { month: '15时', sales: 4200, cost: 2800, profit: 1400 },
      { month: '18时', sales: 5800, cost: 3900, profit: 1900 },
      { month: '21时', sales: 3200, cost: 2100, profit: 1100 },
    ],
    '本周': [
      { month: '周一', sales: 28000, cost: 18000, profit: 10000 },
      { month: '周二', sales: 31000, cost: 20500, profit: 10500 },
      { month: '周三', sales: 33000, cost: 22000, profit: 11000 },
      { month: '周四', sales: 35000, cost: 23500, profit: 11500 },
      { month: '周五', sales: 38000, cost: 25500, profit: 12500 },
      { month: '周六', sales: 42000, cost: 28000, profit: 14000 },
      { month: '周日', sales: 20000, cost: 13500, profit: 6500 },
    ],
    '本月': [
      { month: '1月', sales: 420000, cost: 280000, profit: 140000 },
      { month: '2月', sales: 480000, cost: 320000, profit: 160000 },
      { month: '3月', sales: 520000, cost: 350000, profit: 170000 },
      { month: '4月', sales: 610000, cost: 410000, profit: 200000 },
      { month: '5月', sales: 580000, cost: 390000, profit: 190000 },
      { month: '6月', sales: 670000, cost: 450000, profit: 220000 },
      { month: '7月', sales: 730000, cost: 490000, profit: 240000 },
      { month: '8月', sales: 690000, cost: 460000, profit: 230000 },
      { month: '9月', sales: 780000, cost: 520000, profit: 260000 },
      { month: '10月', sales: 840000, cost: 560000, profit: 280000 },
      { month: '11月', sales: 910000, cost: 610000, profit: 300000 },
      { month: '12月', sales: 980000, cost: 650000, profit: 330000 },
    ],
    '本季度': [
      { month: '第1周', sales: 210000, cost: 140000, profit: 70000 },
      { month: '第2周', sales: 230000, cost: 155000, profit: 75000 },
      { month: '第3周', sales: 250000, cost: 168000, profit: 82000 },
      { month: '第4周', sales: 280000, cost: 188000, profit: 92000 },
      { month: '第5周', sales: 270000, cost: 182000, profit: 88000 },
      { month: '第6周', sales: 290000, cost: 195000, profit: 95000 },
      { month: '第7周', sales: 310000, cost: 208000, profit: 102000 },
      { month: '第8周', sales: 295000, cost: 198000, profit: 97000 },
      { month: '第9周', sales: 315000, cost: 212000, profit: 103000 },
      { month: '第10周', sales: 330000, cost: 222000, profit: 108000 },
      { month: '第11周', sales: 350000, cost: 235000, profit: 115000 },
      { month: '第12周', sales: 310000, cost: 208000, profit: 102000 },
    ],
  };
  return configs[range];
};

const generateInventoryAlerts = (range: DateRange) => {
  const baseAlerts = [
    { id: 1, product: '联想笔记本电脑', sku: 'NB-2024-001', stock: 45, safeStock: 100, status: '库存不足', severity: 'medium', value: 224955 },
    { id: 2, product: 'iPhone 15 Pro', sku: 'PH-2024-002', stock: 23, safeStock: 50, status: '严重不足', severity: 'high', value: 206977 },
    { id: 3, product: 'A4打印纸', sku: 'OF-2024-003', stock: 156, safeStock: 200, status: '库存不足', severity: 'medium', value: 3900 },
    { id: 4, product: '办公椅', sku: 'FU-2024-004', stock: 78, safeStock: 50, status: '正常', severity: 'low', value: 46722 },
    { id: 5, product: '订书机', sku: 'OF-2024-008', stock: 89, safeStock: 80, status: '正常', severity: 'low', value: 1335 },
  ];

  const multipliers = {
    '今日': 0.3,
    '本周': 0.5,
    '本月': 1,
    '本季度': 1.5,
  };

  const multiplier = multipliers[range];
  
  return baseAlerts.map(alert => ({
    ...alert,
    stock: Math.floor(alert.stock * multiplier),
    value: Math.floor(alert.value * multiplier),
  })).filter(alert => {
    if (range === '今日') return alert.severity === 'high';
    if (range === '本周') return alert.severity !== 'low';
    return true;
  });
};

const generateTopProducts = (range: DateRange) => {
  const configs = {
    '今日': [
      { rank: 1, name: 'iPhone 15 Pro', sales: 8, amount: 71992, growth: 25.0 },
      { rank: 2, name: '联想笔记本电脑', sales: 6, amount: 29994, growth: 18.5 },
      { rank: 3, name: '鼠标', sales: 42, amount: 2478, growth: 12.3 },
      { rank: 4, name: '键盘', sales: 28, amount: 4452, growth: 8.7 },
      { rank: 5, name: 'A4打印纸', sales: 35, amount: 875, growth: 5.2 },
    ],
    '本周': [
      { rank: 1, name: 'iPhone 15 Pro', sales: 45, amount: 404955, growth: 22.8 },
      { rank: 2, name: '联想笔记本电脑', sales: 38, amount: 189962, growth: 16.2 },
      { rank: 3, name: '鼠标', sales: 186, amount: 10974, growth: 10.5 },
      { rank: 4, name: '键盘', sales: 145, amount: 23055, growth: 9.8 },
      { rank: 5, name: '办公椅', sales: 52, amount: 31148, growth: 7.3 },
    ],
    '本月': [
      { rank: 1, name: 'iPhone 15 Pro', sales: 98, amount: 881902, growth: 22.5 },
      { rank: 2, name: '联想笔记本电脑', sales: 156, amount: 779844, growth: 15.2 },
      { rank: 3, name: '鼠标', sales: 456, amount: 26904, growth: 8.7 },
      { rank: 4, name: '键盘', sales: 342, amount: 54378, growth: 12.3 },
      { rank: 5, name: '办公椅', sales: 189, amount: 113211, growth: -3.2 },
    ],
    '本季度': [
      { rank: 1, name: 'iPhone 15 Pro', sales: 294, amount: 2645706, growth: 28.3 },
      { rank: 2, name: '联想笔记本电脑', sales: 468, amount: 2339532, growth: 19.8 },
      { rank: 3, name: '鼠标', sales: 1368, amount: 80712, growth: 15.2 },
      { rank: 4, name: '键盘', sales: 1026, amount: 163134, growth: 18.7 },
      { rank: 5, name: '办公椅', sales: 567, amount: 339633, growth: 5.8 },
    ],
  };
  return configs[range];
};

const costDistribution = [
  { name: '采购成本', value: 45, color: '#06B6D4' },
  { name: '仓储成本', value: 18, color: '#3B82F6' },
  { name: '物流成本', value: 15, color: '#10B981' },
  { name: '人力成本', value: 12, color: '#8B5CF6' },
  { name: '其他成本', value: 10, color: '#F59E0B' },
];

// --- State ---
const theme = ref('light'); // Default to light, can be extended to be reactive from a store
const dateRange = ref<DateRange>('本月');
const isRefreshing = ref(false);
const searchTerm = ref('');
const sortBy = ref<SortField>('amount');
const sortOrder = ref<SortOrder>('desc');
const selectedItems = ref<number[]>([]);

// --- Computed Data ---
const kpiData = computed(() => generateKPIData(dateRange.value));
const salesData = computed(() => generateMonthlySales(dateRange.value));
const inventoryData = computed(() => generateInventoryAlerts(dateRange.value));
const topProductsData = computed(() => generateTopProducts(dateRange.value));

const filteredInventory = computed(() => {
  return inventoryData.value.filter(item =>
    item.product.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
    item.sku.toLowerCase().includes(searchTerm.value.toLowerCase())
  );
});

const sortedTopProducts = computed(() => {
  return [...topProductsData.value].sort((a, b) => {
    const aValue = a[sortBy.value];
    const bValue = b[sortBy.value];
    if (sortOrder.value === 'asc') {
      return aValue > bValue ? 1 : -1;
    }
    return aValue < bValue ? 1 : -1;
  });
});

// --- Style Helpers ---
const textPrimary = computed(() => theme.value === 'dark' ? 'text-white' : 'text-[#111827]');
const textSecondary = computed(() => theme.value === 'dark' ? 'text-slate-400' : 'text-[#6B7280]');
const cardBg = computed(() => theme.value === 'dark'
  ? 'bg-gradient-to-br from-slate-800/50 to-slate-900/50 border-slate-700/50'
  : 'bg-white border-[#E5E7EB]');
const borderClass = computed(() => theme.value === 'dark' ? 'border-slate-700' : 'border-[#E5E7EB]');
const rowHover = computed(() => theme.value === 'dark' ? 'hover:bg-slate-700/30' : 'hover:bg-[#F9FAFB]');
const zebraStripe = computed(() => theme.value === 'dark' ? 'bg-slate-800/20' : 'bg-[#F9FAFB]');
const inputBg = computed(() => theme.value === 'dark' ? 'bg-slate-700 border-slate-600' : 'bg-[#F9FAFB] border-[#D1D5DB]');
const gridColor = computed(() => theme.value === 'dark' ? '#334155' : '#E5E7EB');
const axisColor = computed(() => theme.value === 'dark' ? '#94A3B8' : '#6B7280');

// --- Methods ---
const handleRefresh = () => {
  isRefreshing.value = true;
  setTimeout(() => {
    isRefreshing.value = false;
    const now = new Date().toLocaleTimeString('zh-CN');
    alert(`数据已刷新！\n刷新时间: ${now}\n数据范围: ${dateRange.value}`);
  }, 1000);
};

const handleExport = () => {
  const exportData = {
    时间范围: dateRange.value,
    导出时间: new Date().toLocaleString('zh-CN'),
    销售额: `¥${kpiData.value.sales.value.toLocaleString()}`,
    采购额: `¥${kpiData.value.purchase.value.toLocaleString()}`,
    库存总值: `¥${kpiData.value.inventory.value.toLocaleString()}`,
    预警数量: kpiData.value.alerts.value,
    销售趋势: salesData.value,
    库存预警: inventoryData.value,
    热销商品: topProductsData.value,
  };
  
  const flatData = salesData.value.map((item, index) => ({
    序号: index + 1,
    时间: item.month,
    销售额: item.sales,
    成本: item.cost,
    利润: item.profit,
  }));
  
  // exportToCSV(flatData, `进销存看板_${dateRange.value}`);
  alert(`导出数据：进销存看板_${dateRange.value}`);
};

const handleSort = (field: SortField) => {
  if (sortBy.value === field) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortBy.value = field;
    sortOrder.value = 'desc';
  }
};

const handleKPIClick = (key: string, value: any) => {
  alert(`查看${key}详情\n此处对接后端详情接口\n当前值: ${key === '库存预警' ? value : `¥${value.toLocaleString()}`}\n变化: ${value}`);
};

const handleViewDetail = (product: TopProduct) => {
  alert(`查看商品详情
商品: ${product.name}
销量: ${product.sales}
销售额: ¥${product.amount.toLocaleString()}
增长率: ${product.growth}%

此处对接后端商品详情接口`);
};

const handleQuickOrder = (product: TopProduct) => {
  alert(`快速下单
商品: ${product.name}
建议订购量: ${Math.ceil(product.sales * 0.3)}

此处对接后端下单接口`);
};

// --- Chart Options ---
const getSparklineOption = (data: number[], color: string): EChartsOption => ({
  grid: { top: 0, bottom: 0, left: 0, right: 0 },
  xAxis: { type: 'category', show: false, boundaryGap: false },
  yAxis: { type: 'value', show: false, min: 'dataMin' },
  series: [{
    type: 'line',
    data: data,
    smooth: true,
    showSymbol: false,
    lineStyle: { color: color, width: 2 },
    areaStyle: {
      color: {
        type: 'linear',
        x: 0, y: 0, x2: 0, y2: 1,
        colorStops: [
          { offset: 0, color: color },
          { offset: 1, color: 'rgba(255,255,255,0)' }
        ]
      },
      opacity: 0.1
    }
  }]
});

const salesTrendOption = computed<EChartsOption>(() => ({
  grid: { top: 30, right: 20, bottom: 20, left: 40, containLabel: true },
  tooltip: {
    trigger: 'axis',
    backgroundColor: theme.value === 'dark' ? '#1E293B' : '#FFFFFF',
    borderColor: theme.value === 'dark' ? '#334155' : '#E5E7EB',
    textStyle: {
      color: theme.value === 'dark' ? '#fff' : '#111827',
      fontWeight: 500,
    },
    formatter: (params: any) => {
      const p = params[0];
      return `${p.name}<br/>${p.seriesName}: ¥${p.value.toLocaleString()}`;
    }
  },
  legend: {
    top: 0,
    textStyle: { color: axisColor.value }
  },
  xAxis: {
    type: 'category',
    data: salesData.value.map(d => d.month),
    axisLine: { lineStyle: { color: axisColor.value } },
    axisLabel: { color: axisColor.value }
  },
  yAxis: {
    type: 'value',
    axisLine: { show: false },
    axisTick: { show: false },
    splitLine: { lineStyle: { color: gridColor.value } },
    axisLabel: {
      color: axisColor.value,
      formatter: (value: number) => `¥${(value / 1000).toFixed(0)}k`
    }
  },
  series: [
    {
      name: '销售额',
      type: 'line',
      data: salesData.value.map(d => d.sales),
      smooth: false,
      symbol: 'circle',
      symbolSize: 4,
      itemStyle: { color: '#06B6D4' },
      lineStyle: { width: 3, color: '#06B6D4' }
    },
    {
      name: '成本',
      type: 'line',
      data: salesData.value.map(d => d.cost),
      smooth: false,
      symbol: 'circle',
      symbolSize: 4,
      itemStyle: { color: '#F59E0B' },
      lineStyle: { width: 3, color: '#F59E0B' }
    },
    {
      name: '利润',
      type: 'line',
      data: salesData.value.map(d => d.profit),
      smooth: false,
      symbol: 'circle',
      symbolSize: 4,
      itemStyle: { color: '#10B981' },
      lineStyle: { width: 3, color: '#10B981' }
    }
  ]
}));

const costDistributionOption = computed<EChartsOption>(() => ({
  tooltip: {
    trigger: 'item',
    backgroundColor: theme.value === 'dark' ? '#1E293B' : '#FFFFFF',
    borderColor: theme.value === 'dark' ? '#334155' : '#E2E8F0',
    borderRadius: 8,
    textStyle: { 
      color: theme.value === 'dark' ? '#fff' : '#0F172A' 
    },
    formatter: (params: any) => `${params.value}%`
  },
  legend: {
    orient: 'vertical',
    bottom: 'bottom',
    icon: 'circle',
    textStyle: {
      fontSize: 12,
      color: theme.value === 'dark' ? '#94A3B8' : '#6B7280'
    }
  },
  series: [
    {
      name: '成本分布',
      type: 'pie',
      radius: ['60%', '90%'],
      center: ['50%', '50%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 0,
        borderColor: theme.value === 'dark' ? '#1E293B' : '#fff',
        borderWidth: 0
      },
      label: { show: false },
      data: costDistribution.map(item => ({
        value: item.value,
        name: item.name,
        itemStyle: { color: item.color }
      }))
    }
  ]
}));
</script>

<template>
  <div class="p-4 sm:p-6 lg:p-8 max-w-[1920px] mx-auto">
    <!-- Header with Actions -->
    <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4 mb-6 lg:mb-8">
      <div class="flex-shrink-0">
        <h1 :class="['text-xl sm:text-2xl font-semibold mb-1', textPrimary]">数据看板</h1>
        <p :class="['text-xs sm:text-sm', textSecondary]">实时监控进销存核心指标 - 当前范围: <span class="font-medium text-cyan-500">{{ dateRange }}</span></p>
      </div>

      <div class="flex flex-wrap items-center gap-2 sm:gap-3">
        <!-- Date Range Selector -->
        <div class="flex items-center gap-1.5 sm:gap-2 flex-wrap">
          <el-icon :size="18" :class="textSecondary" class="flex-shrink-0"><Calendar /></el-icon>
          <button
            v-for="range in (['今日', '本周', '本月', '本季度'] as const)"
            :key="range"
            @click="dateRange = range"
            :class="[
              'px-2.5 sm:px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium transition-all whitespace-nowrap',
              dateRange === range
                ? 'bg-cyan-500 text-white shadow-md'
                : theme === 'dark'
                ? 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                : 'bg-white text-[#374151] hover:bg-[#F3F4F6] border border-[#E5E7EB]'
            ]"
          >
            {{ range }}
          </button>
        </div>

        <button
          @click="handleRefresh"
          :disabled="isRefreshing"
          :class="[
            'flex items-center gap-1.5 sm:gap-2 px-3 sm:px-4 py-2 rounded-lg text-xs sm:text-sm font-medium transition-all whitespace-nowrap',
            theme === 'dark'
              ? 'bg-slate-800 hover:bg-slate-700 text-slate-300'
              : 'bg-white hover:bg-[#F3F4F6] text-[#374151] border border-[#E5E7EB]',
            isRefreshing ? 'opacity-50' : ''
          ]"
        >
          <el-icon :class="isRefreshing ? 'is-loading' : ''" :size="16"><Refresh /></el-icon>
          <span class="hidden sm:inline">刷新</span>
        </button>

        <button
          @click="handleExport"
          class="flex items-center gap-1.5 sm:gap-2 px-3 sm:px-4 py-2 bg-cyan-500 hover:bg-cyan-600 text-white rounded-lg text-xs sm:text-sm font-medium transition-all shadow-md whitespace-nowrap"
        >
          <el-icon :size="16"><Download /></el-icon>
          <span class="hidden sm:inline">导出报表</span>
        </button>
      </div>
    </div>

    <!-- Row 1: KPI Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 sm:gap-5 lg:gap-6 mb-6 lg:mb-8">
      <div 
        v-for="(kpi, key) in {
          '销售额': { ...kpiData.sales, accentColor: '#06B6D4' },
          '采购额': { ...kpiData.purchase, accentColor: '#10B981' },
          '库存总值': { ...kpiData.inventory, accentColor: '#3B82F6' },
          '库存预警': { ...kpiData.alerts, accentColor: '#F59E0B' }
        }" 
        :key="key"
        :class="['relative overflow-hidden rounded-xl border p-6 hover:border-cyan-400 hover:shadow-lg transition-all cursor-pointer group', cardBg]"
        @click="handleKPIClick(key, kpi.value)"
      >
        <!-- Neon Glow Effect -->
        <div 
          class="absolute top-0 right-0 w-32 h-32 rounded-full blur-3xl opacity-20"
          :style="{ backgroundColor: kpi.accentColor }"
        ></div>

        <!-- Content -->
        <div class="relative">
          <div class="flex items-start justify-between mb-4">
            <div>
              <p :class="['text-sm font-medium mb-1', textSecondary]">{{ key }}</p>
              <h3 :class="['text-2xl font-bold tracking-tight', textPrimary]">
                {{ key === '库存预警' ? kpi.value : `¥${kpi.value.toLocaleString()}` }}
              </h3>
            </div>
            <div 
              class="w-10 h-10 rounded-lg flex items-center justify-center"
              :style="{ backgroundColor: `${kpi.accentColor}20` }"
            >
          <el-icon :size="20" :color="kpi.accentColor">
            <Top v-if="kpi.change >= 0" />
            <Bottom v-else />
          </el-icon>
            </div>
          </div>

          <!-- Sparkline -->
          <div class="mb-3 -mx-2 h-[40px]">
            <BaseChart :option="getSparklineOption(kpi.data, kpi.accentColor)" />
          </div>

          <!-- Change Indicator -->
          <div class="flex items-center gap-2">
            <span
              class="text-sm font-semibold"
              :style="{ color: kpi.change >= 0 ? '#10B981' : '#EF4444' }"
            >
              {{ kpi.change >= 0 ? '+' : '' }}{{ kpi.change }}{{ key === '库存预警' ? '' : '%' }}
            </span>
            <span :class="['text-xs font-medium', theme === 'dark' ? 'text-slate-500' : 'text-[#9CA3AF]']">较上期</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Row 2: Charts -->
    <div class="grid grid-cols-1 xl:grid-cols-3 gap-4 sm:gap-5 lg:gap-6 mb-6 lg:mb-8">
      <div class="xl:col-span-2">
        <!-- SalesTrendChart Inline -->
        <div :class="['rounded-xl border p-6 shadow-sm', cardBg]">
          <div class="mb-6">
            <h3 :class="['text-lg font-semibold mb-1', textPrimary]">
              {{ dateRange === '今日' ? '今日销售趋势' : dateRange === '本周' ? '本周销售趋势' : dateRange === '本月' ? '本月销售趋势' : '本季度销售趋势' }}
            </h3>
            <p :class="['text-sm font-medium', textSecondary]">销售额、成本与利润对比</p>
          </div>
          <div class="h-[300px]">
            <BaseChart :option="salesTrendOption" />
          </div>
        </div>
      </div>
      <div class="xl:col-span-1">
        <!-- CostDistributionChart Inline -->
        <div :class="['rounded-xl border p-6 shadow-sm h-full', cardBg]">
          <div class="mb-6">
            <h3 :class="['text-lg font-semibold mb-1', textPrimary]">成本分布</h3>
            <p :class="['text-sm font-medium', textSecondary]">按类型分类</p>
          </div>
          
          <div class="h-[300px]">
             <BaseChart :option="costDistributionOption" />
          </div>
        </div>
      </div>
    </div>

    <!-- Row 3: Tables -->
    <div class="grid grid-cols-1 xl:grid-cols-2 gap-4 sm:gap-5 lg:gap-6 mb-6">
      <!-- InventoryTable Inline -->
      <div :class="['rounded-xl border overflow-hidden shadow-sm', cardBg]">
        <!-- Header -->
        <div class="p-6 border-b" :class="borderClass">
          <div class="flex items-center justify-between mb-3">
            <div>
              <h3 :class="['text-lg font-semibold mb-1', textPrimary]">库存预警</h3>
              <p :class="['text-sm font-medium', textSecondary]">需要关注的商品 - {{ dateRange }}</p>
            </div>
            <div class="flex items-center gap-2 px-4 py-2 bg-red-500/10 border border-red-500/30 rounded-lg">
              <el-icon :size="16" class="text-red-500"><Warning /></el-icon>
              <span class="text-sm font-semibold text-red-600">{{ filteredInventory.length }} 条预警</span>
            </div>
          </div>

          <!-- Actions Bar -->
          <div class="flex items-center gap-3 flex-wrap">
            <div class="relative flex-1 min-w-[200px]">
              <el-icon :size="16" :class="['absolute left-3 top-1/2 -translate-y-1/2', textSecondary]"><Search /></el-icon>
              <input
                v-model="searchTerm"
                type="text"
                placeholder="搜索商品名称或SKU..."
                :class="[
                  'w-full pl-9 pr-4 py-2 border rounded-lg text-sm font-medium placeholder-[#9CA3AF] focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500',
                  inputBg,
                  textPrimary
                ]"
              />
            </div>
            
            <button
              @click="handleRefresh"
              :disabled="isRefreshing"
              :class="[
                'flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all',
                theme === 'dark'
                  ? 'bg-slate-700 hover:bg-slate-600 text-slate-300'
                  : 'bg-white hover:bg-[#F3F4F6] text-[#374151] border border-[#E5E7EB]',
                isRefreshing ? 'opacity-50' : ''
              ]"
            >
              <el-icon :size="16" :class="isRefreshing ? 'is-loading' : ''"><Refresh /></el-icon>
              <span>刷新</span>
            </button>

            <button
              class="flex items-center gap-2 px-3 py-2 bg-green-500/20 text-green-700 hover:bg-green-500/30 border border-green-500/30 rounded-lg text-sm font-medium transition-all"
            >
              <el-icon :size="16"><Download /></el-icon>
              <span>导出</span>
            </button>

            <button
              class="flex items-center gap-2 px-3 py-2 bg-cyan-500/20 text-cyan-700 hover:bg-cyan-500/30 border border-cyan-500/30 rounded-lg text-sm font-medium transition-all"
            >
              <el-icon :size="16"><Plus /></el-icon>
              <span>添加</span>
            </button>
          </div>
        </div>
        <!-- Table -->
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead :class="theme === 'dark' ? 'bg-slate-800/50' : 'bg-[#F3F4F6]'">
              <tr>
                <th :class="['px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider', textSecondary]">产品名称</th>
                <th :class="['px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider', textSecondary]">当前库存</th>
                <th :class="['px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider', textSecondary]">状态</th>
                <th :class="['px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider', textSecondary]">库存价值</th>
                <th :class="['px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider', textSecondary]">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(item, index) in filteredInventory" 
                :key="item.id"
                :class="[
                  'border-t transition-colors',
                  theme === 'dark' ? 'border-slate-700/50' : 'border-[#E5E7EB]',
                  rowHover,
                  index % 2 === 0 ? zebraStripe : 'bg-transparent'
                ]"
              >
                <td class="px-6 py-4">
                  <div class="flex items-center gap-3">
                    <div :class="['w-8 h-8 rounded-lg flex items-center justify-center', theme === 'dark' ? 'bg-slate-700/50' : 'bg-[#F3F4F6]']">
                      <el-icon :size="16" :class="textSecondary"><Box /></el-icon>
                    </div>
                    <div>
                      <span :class="['text-sm font-semibold', textPrimary]">{{ item.product }}</span>
                      <p :class="['text-xs font-medium', textSecondary]">{{ item.sku }}</p>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4">
                  <div class="flex items-center gap-2">
                    <span :class="['text-sm font-bold', textPrimary]">{{ item.stock }}</span>
                    <el-icon :size="14" class="text-red-500"><Bottom /></el-icon>
                  </div>
                  <p :class="['text-xs font-medium', textSecondary]">安全值: {{ item.safeStock }}</p>
                </td>
                <td class="px-6 py-4">
                  <span
                    :class="[
                      'inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border',
                      item.severity === 'high'
                        ? 'bg-red-500/10 text-red-700 border-red-500/30'
                        : item.severity === 'medium'
                        ? 'bg-yellow-500/10 text-yellow-700 border-yellow-500/30'
                        : 'bg-green-500/10 text-green-700 border-green-500/30'
                    ]"
                  >
                    <el-icon :size="12"><Warning /></el-icon>
                    {{ item.status }}
                  </span>
                </td>
                <td class="px-6 py-4">
                  <span class="text-sm text-cyan-600 font-bold">¥{{ item.value.toLocaleString() }}</span>
                </td>
                <td class="px-6 py-4">
                  <div class="flex items-center gap-2">
                    <button
                      :class="[
                        'p-1.5 rounded-lg transition-colors',
                        theme === 'dark'
                          ? 'hover:bg-slate-700 text-slate-400 hover:text-cyan-400'
                          : 'hover:bg-[#F3F4F6] text-[#6B7280] hover:text-cyan-600'
                      ]"
                      title="编辑"
                    >
                      <el-icon :size="16"><Edit /></el-icon>
                    </button>
                    <button
                      :class="[
                        'p-1.5 rounded-lg transition-colors',
                        theme === 'dark'
                          ? 'hover:bg-slate-700 text-slate-400 hover:text-red-400'
                          : 'hover:bg-[#F3F4F6] text-[#6B7280] hover:text-red-600'
                      ]"
                      title="删除"
                    >
                      <el-icon :size="16"><Delete /></el-icon>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- TopProductsTable Inline -->
      <div :class="['rounded-xl border overflow-hidden shadow-sm', cardBg]">
        <!-- Header -->
        <div class="p-6 border-b" :class="borderClass">
          <div class="flex items-center justify-between mb-3">
            <div>
              <h3 :class="['text-lg font-semibold mb-1', textPrimary]">热销商品排行</h3>
              <p :class="['text-sm font-medium', textSecondary]">{{ dateRange }} TOP5</p>
            </div>
            <div class="flex items-center gap-2 px-4 py-2 bg-cyan-500/10 border border-cyan-500/30 rounded-lg">
              <el-icon :size="16" class="text-cyan-500"><TrophyBase /></el-icon>
              <span class="text-sm text-cyan-700 font-semibold">TOP 5</span>
            </div>
          </div>

          <!-- Sort Options -->
          <div class="flex items-center gap-2">
            <el-icon :size="14" :class="textSecondary"><Filter /></el-icon>
            <span :class="['text-xs font-medium', textSecondary]">排序:</span>
            <button
              @click="handleSort('amount')"
              :class="[
                'px-3 py-1 rounded-lg text-xs font-medium transition-all',
                sortBy === 'amount'
                  ? 'bg-cyan-500/20 text-cyan-700 border border-cyan-500/30'
                  : theme === 'dark'
                  ? 'bg-slate-700 text-slate-400 hover:bg-slate-600'
                  : 'bg-white text-[#6B7280] hover:bg-[#F3F4F6] border border-[#E5E7EB]'
              ]"
            >
              销售额 {{ sortBy === 'amount' ? (sortOrder === 'desc' ? '↓' : '↑') : '' }}
            </button>
            <button
              @click="handleSort('sales')"
              :class="[
                'px-3 py-1 rounded-lg text-xs font-medium transition-all',
                sortBy === 'sales'
                  ? 'bg-cyan-500/20 text-cyan-700 border border-cyan-500/30'
                  : theme === 'dark'
                  ? 'bg-slate-700 text-slate-400 hover:bg-slate-600'
                  : 'bg-white text-[#6B7280] hover:bg-[#F3F4F6] border border-[#E5E7EB]'
              ]"
            >
              销量 {{ sortBy === 'sales' ? (sortOrder === 'desc' ? '↓' : '↑') : '' }}
            </button>
            <button
              @click="handleSort('growth')"
              :class="[
                'px-3 py-1 rounded-lg text-xs font-medium transition-all',
                sortBy === 'growth'
                  ? 'bg-cyan-500/20 text-cyan-700 border border-cyan-500/30'
                  : theme === 'dark'
                  ? 'bg-slate-700 text-slate-400 hover:bg-slate-600'
                  : 'bg-white text-[#6B7280] hover:bg-[#F3F4F6] border border-[#E5E7EB]'
              ]"
            >
              增长率 {{ sortBy === 'growth' ? (sortOrder === 'desc' ? '↓' : '↑') : '' }}
            </button>
          </div>
        </div>
        <!-- Table -->
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead :class="theme === 'dark' ? 'bg-slate-800/50' : 'bg-[#F3F4F6]'">
              <tr>
                <th :class="['px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider', textSecondary]">排名</th>
                <th :class="['px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider', textSecondary]">商品名称</th>
                <th :class="['px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider', textSecondary]">销量</th>
                <th :class="['px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider', textSecondary]">销售额</th>
                <th :class="['px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider', textSecondary]">增长率</th>
                <th :class="['px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider', textSecondary]">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(item, index) in sortedTopProducts" 
                :key="item.rank"
                :class="[
                  'border-t transition-colors',
                  theme === 'dark' ? 'border-slate-700/50' : 'border-[#E5E7EB]',
                  rowHover,
                  index % 2 === 0 ? zebraStripe : 'bg-transparent'
                ]"
              >
                <td class="px-6 py-4">
                  <div class="flex items-center gap-2">
                    <div
                      v-if="item.rank <= 3"
                      :class="[
                        'w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold shadow-md',
                        item.rank === 1
                          ? 'bg-gradient-to-br from-yellow-400 to-yellow-600 text-white'
                          : item.rank === 2
                          ? 'bg-gradient-to-br from-slate-300 to-slate-500 text-white'
                          : 'bg-gradient-to-br from-amber-600 to-amber-800 text-white'
                      ]"
                    >
                      {{ item.rank }}
                    </div>
                    <span v-else :class="['text-sm font-bold ml-2', textSecondary]">{{ item.rank }}</span>
                  </div>
                </td>
                <td class="px-6 py-4">
                  <span :class="['text-sm font-semibold', textPrimary]">{{ item.name }}</span>
                </td>
                <td class="px-6 py-4">
                  <span :class="['text-sm font-bold', textPrimary]">{{ item.sales }}</span>
                  <span :class="['text-xs font-medium ml-1', textSecondary]">件</span>
                </td>
                <td class="px-6 py-4">
                  <span class="text-sm text-cyan-600 font-bold">¥{{ item.amount.toLocaleString() }}</span>
                </td>
                <td class="px-6 py-4">
                  <div class="flex items-center gap-1">
                    <el-icon v-if="item.growth >= 0" :size="14" class="text-green-600"><Top /></el-icon>
                    <el-icon v-else :size="14" class="text-red-600"><Bottom /></el-icon>
                    <span :class="['text-sm font-bold', item.growth >= 0 ? 'text-green-700' : 'text-red-700']">
                      {{ item.growth >= 0 ? '+' : '' }}{{ item.growth }}%
                    </span>
                  </div>
                </td>
                <td class="px-6 py-4">
                  <div class="flex items-center gap-2">
                    <button
                      @click="handleViewDetail(item)"
                      :class="[
                        'p-1.5 rounded-lg transition-colors',
                        theme === 'dark'
                          ? 'hover:bg-slate-700 text-slate-400 hover:text-cyan-400'
                          : 'hover:bg-[#F3F4F6] text-[#6B7280] hover:text-cyan-600'
                      ]"
                      title="查看详情"
                    >
                      <el-icon :size="16"><View /></el-icon>
                    </button>
                    <button
                      @click="handleQuickOrder(item)"
                      :class="[
                        'p-1.5 rounded-lg transition-colors',
                        theme === 'dark'
                          ? 'hover:bg-slate-700 text-slate-400 hover:text-green-400'
                          : 'hover:bg-[#F3F4F6] text-[#6B7280] hover:text-green-600'
                      ]"
                      title="快速下单"
                    >
                      <el-icon :size="16"><ShoppingCart /></el-icon>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Tailwind utility classes - strictly matching React version */
</style>
