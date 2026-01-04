<script setup lang="ts">
import { ref, computed, nextTick } from 'vue';
import { Document, Download, View, Calendar, Filter, Plus, Search, Close, ChatDotRound, Promotion, DataAnalysis } from '@element-plus/icons-vue';

// 报表数据类型
interface ChartData {
  type: string;
  value: number;
  growth: number;
}

interface TopProduct {
  name: string;
  sales: number;
  amount: number;
}

interface Alert {
  product: string;
  status: string;
  stock: number;
}

interface Supplier {
  name: string;
  amount: number;
  orders: number;
}

interface Customer {
  name: string;
  amount: number;
  level: string;
}

interface ReportData {
  summary?: string;
  charts?: ChartData[];
  topProducts?: TopProduct[];
  alerts?: Alert[];
  suppliers?: Supplier[];
  customers?: Customer[];
}

interface Report {
  id: number;
  name: string;
  category: string;
  createDate: string;
  size: string;
  status: 'completed' | 'processing' | 'scheduled';
  downloads: number;
  data?: ReportData;
}

interface Message {
  id: number;
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
}

const theme = ref<'light' | 'dark'>('light');

const mockReports: Report[] = [
  {
    id: 1,
    name: '2026年1月销售分析报表',
    category: '销售报表',
    createDate: '2026-01-03',
    size: '2.4 MB',
    status: 'completed',
    downloads: 45,
    data: {
      summary: '本月总销售额为￥980,000，较上月增长15.8%。主要增长来自电子产品类别，其中笔记本电脑和手机销售额占比最高。',
      charts: [
        { type: 'sales', value: 980000, growth: 15.8 },
        { type: 'orders', value: 342, growth: 12.3 },
      ],
      topProducts: [
        { name: 'iPhone 15 Pro', sales: 98, amount: 881902 },
        { name: '联想笔记本电脑', sales: 156, amount: 779844 },
      ],
    },
  },
  {
    id: 2,
    name: '库存周转率分析报告',
    category: '库存报表',
    createDate: '2026-01-02',
    size: '1.8 MB',
    status: 'completed',
    downloads: 32,
    data: {
      summary: '本月库存周转率为2.3次，库存周转天数为13天。电子产品周转最快，食品饮料库存积压较多。',
      charts: [
        { type: 'turnover', value: 2.3, growth: 5.2 },
        { type: 'days', value: 13, growth: -8.1 },
      ],
      alerts: [
        { product: '联想笔记本电脑', status: '库存不足', stock: 45 },
        { product: 'iPhone 15 Pro', status: '严重不足', stock: 23 },
      ],
    },
  },
  {
    id: 3,
    name: '采购订单执行报表',
    category: '采购报表',
    createDate: '2026-01-01',
    size: '3.2 MB',
    status: 'completed',
    downloads: 28,
    data: {
      summary: '本月共执行采购订南35笔，总采购金额￥650,000。到货准时率92%，质量合格率98%。',
      charts: [
        { type: 'purchase', value: 650000, growth: 12.3 },
        { type: 'ontime', value: 92, growth: 3.5 },
      ],
      suppliers: [
        { name: '深圳科技有限公司', amount: 329950, orders: 12 },
        { name: '上海办公用品批发', amount: 125000, orders: 8 },
      ],
    },
  },
  {
    id: 4,
    name: '客户销售排行榜',
    category: '客户报表',
    createDate: '2025-12-31',
    size: '4.1 MB',
    status: 'completed',
    downloads: 67,
    data: {
      summary: 'VIP客户贡献了68%的销售额，前10大客户占比达到82%。建议加强大客户关系维护。',
      charts: [
        { type: 'vip', value: 68, growth: 8.2 },
        { type: 'top10', value: 82, growth: 5.1 },
      ],
      customers: [
        { name: '阿里巴巴', amount: 249950, level: 'VIP' },
        { name: '腾讯科技', amount: 269970, level: 'VIP' },
      ],
    },
  },
  {
    id: 5,
    name: '利润分析月报',
    category: '财务报表',
    createDate: '2025-12-30',
    size: '2.9 MB',
    status: 'processing',
    downloads: 0,
  },
  {
    id: 6,
    name: '商品毛利率分析',
    category: '财务报表',
    createDate: '2025-12-29',
    size: '1.5 MB',
    status: 'completed',
    downloads: 51,
    data: {
      summary: '整体毛利率为33.6%，电子产品毛利率最高达38%，食品饮料毛利率较低为18%。',
      charts: [
        { type: 'margin', value: 33.6, growth: 2.3 },
      ],
    },
  },
  {
    id: 7,
    name: '仓库绩效报表',
    category: '运营报表',
    createDate: '2025-12-28',
    size: '0.9 MB',
    status: 'completed',
    downloads: 23,
    data: {
      summary: '本月仓库整体运营效率提升12%，出库准确率达99.2%，平均拣货时长缩短至5分钟。',
      charts: [
        { type: 'efficiency', value: 95, growth: 12 },
        { type: 'accuracy', value: 99.2, growth: 0.8 },
      ],
    },
  },
  {
    id: 8,
    name: '季度销售预测',
    category: '销售报表',
    createDate: '2026-01-10',
    size: '-',
    status: 'scheduled',
    downloads: 0,
  },
];

const categories = ['全部', '销售报表', '库存报表', '财务报表', '运营报表', '客户报表', '采购报表'];

const selectedCategory = ref('全部');
const searchTerm = ref('');

// 报表预览状态
const previewReport = ref<Report | null>(null);
const showChat = ref(false);
const messages = ref<Message[]>([]);
const inputValue = ref('');
const isTyping = ref(false);
const messagesContainer = ref<HTMLElement | null>(null);

const filteredReports = computed(() => {
  return mockReports.filter((report) => {
    const matchesCategory = selectedCategory.value === '全部' || report.category === selectedCategory.value;
    const matchesSearch = report.name.toLowerCase().includes(searchTerm.value.toLowerCase());
    return matchesCategory && matchesSearch;
  });
});

// 样式计算
const textPrimary = computed(() => theme.value === 'dark' ? 'text-white' : 'text-[#0F172A]');
const textSecondary = computed(() => theme.value === 'dark' ? 'text-slate-400' : 'text-slate-600');
const cardBg = computed(() => theme.value === 'dark'
  ? 'bg-gradient-to-br from-slate-800/50 to-slate-900/50 border-slate-700/50'
  : 'bg-white border-slate-200 shadow-sm');
const inputBg = computed(() => theme.value === 'dark' ? 'bg-slate-800/50 border-slate-700' : 'bg-slate-50 border-slate-300');
const modalBg = computed(() => theme.value === 'dark' ? 'bg-[#1E293B]' : 'bg-white');
const borderClass = computed(() => theme.value === 'dark' ? 'border-slate-700' : 'border-slate-200');
const modalCardBg = computed(() => theme.value === 'dark' ? 'bg-slate-800/50 border-slate-700' : 'bg-slate-50 border-slate-200');

const getStatusBadge = (status: Report['status']) => {
  switch (status) {
    case 'completed':
      return { class: 'bg-green-500/10 text-green-600 border-green-500/30', text: '已完成' };
    case 'processing':
      return { class: 'bg-yellow-500/10 text-yellow-600 border-yellow-500/30', text: '生成中' };
    case 'scheduled':
      return { class: 'bg-blue-500/10 text-blue-600 border-blue-500/30', text: '已预约' };
  }
};

// 获取图表指标名称
const getChartLabel = (type: string) => {
  const labels: Record<string, string> = {
    sales: '销售额',
    orders: '订单数',
    turnover: '周转率',
    days: '周转天数',
    purchase: '采购额',
    ontime: '准时率',
    vip: 'VIP占比',
    top10: 'TOP10占比',
    margin: '毛利率',
    efficiency: '运营效率',
    accuracy: '出库准确率',
  };
  return labels[type] || '指标';
};

// 格式化图表数值
const formatChartValue = (chart: ChartData) => {
  if (chart.type === 'sales' || chart.type === 'purchase') {
    return `￥${chart.value.toLocaleString()}`;
  }
  if (['margin', 'vip', 'top10', 'ontime', 'efficiency', 'accuracy'].includes(chart.type)) {
    return `${chart.value}%`;
  }
  if (chart.type === 'turnover') {
    return `${chart.value}次`;
  }
  if (chart.type === 'days') {
    return `${chart.value}天`;
  }
  return String(chart.value);
};

// 打开报表预览
const handlePreview = (report: Report) => {
  previewReport.value = report;
  showChat.value = false;
  messages.value = [
    {
      id: 1,
      type: 'ai',
      content: `我已加载《${report.name}》的数据，可以帮您分析报表内容、解读数据趋势、提供决策建议。请问有什么想了解的？`,
      timestamp: new Date(),
    },
  ];
  inputValue.value = '';
};

// 关闭报表预览
const closePreview = () => {
  previewReport.value = null;
  showChat.value = false;
};

// 切换AI分析面板
const toggleChat = () => {
  showChat.value = !showChat.value;
};

// AI快速提问
const suggestedQuestions = [
  '帮我总结一下报表重点',
  '本期销售情况如何？',
  '哪些商品库存告急？',
  '给我一些优化建议',
];

// 生成AI回复
const generateAIResponse = (question: string, report: Report): string => {
  const lowerQ = question.toLowerCase();
  
  if (lowerQ.includes('总结') || lowerQ.includes('概况') || lowerQ.includes('汇总')) {
    return report.data?.summary || '根据报表数据分析，本期整体表现良好，主要指标均达到预期目标。';
  }
  
  if (lowerQ.includes('销售') || lowerQ.includes('收入')) {
    return '本月销售额达到￥980,000，同比增长15.8%。其中电子产品类销售占比最高，达到45%。建议继续加强电子产品的市场推广力度。';
  }
  
  if (lowerQ.includes('库存') || lowerQ.includes('存货')) {
    return '当前有15个SKU出现库存预警，其中2个严重不足。建议优先补充：联想笔记本电脑（当前45台，安全库存100台）、iPhone 15 Pro（当前23台，安全库存50台）。';
  }
  
  if (lowerQ.includes('利润') || lowerQ.includes('毛利')) {
    return '本月毛利率为33.6%，较上月提升2.3个百分点。电子产品毛利率最高达38%，建议扩大电子产品的销售规模以提升整体利润水平。';
  }
  
  if (lowerQ.includes('客户') || lowerQ.includes('top') || lowerQ.includes('排名')) {
    return 'VIP客户贡献了68%的销售额。前三大客户分别是：腾讯科技（￥269,970）、阿里巴巴（￥249,950）、字节跳动（￥47,910）。建议加强大客户关系维护，提供定制化服务。';
  }
  
  if (lowerQ.includes('建议') || lowerQ.includes('优化') || lowerQ.includes('改进')) {
    return '基于当前数据分析，我建议：\n1. 加快库存周转，减少资金占用\n2. 优化采购计划，避免库存积压\n3. 加强大客户关系维护\n4. 提升高毛利商品的销售占比\n5. 建立预警机制，及时补充畅销品库存';
  }
  
  if (lowerQ.includes('趋势') || lowerQ.includes('预测')) {
    return '从近12个月的数据趋势来看，销售额呈现稳定上升态势，月均增长率约12%。预计下月销售额将达到￥1,100,000左右。建议提前做好备货准备。';
  }
  
  return '基于报表数据，我可以为您分析销售趋势、库存状况、客户分布、利润情况等维度。您可以问我：\n• 本月销售情况如何？\n• 哪些商品需要补货？\n• 利润率怎么样？\n• 重点客户有哪些？\n• 有什么优化建议？';
};

// 发送消息
const handleSendMessage = () => {
  if (!inputValue.value.trim() || !previewReport.value) return;

  const userMessage: Message = {
    id: messages.value.length + 1,
    type: 'user',
    content: inputValue.value,
    timestamp: new Date(),
  };
  messages.value.push(userMessage);
  const question = inputValue.value;
  inputValue.value = '';
  isTyping.value = true;

  // 滚动到底部
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });

  setTimeout(() => {
    const aiMessage: Message = {
      id: messages.value.length + 1,
      type: 'ai',
      content: generateAIResponse(question, previewReport.value!),
      timestamp: new Date(),
    };
    messages.value.push(aiMessage);
    isTyping.value = false;
    
    nextTick(() => {
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
      }
    });
  }, 1500);
};

// 快速提问
const handleQuickQuestion = (question: string) => {
  inputValue.value = question;
  nextTick(() => {
    handleSendMessage();
  });
};

// 格式化时间
const formatTime = (date: Date) => {
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
};

const handleDownload = (report: Report) => {
  alert(`下载报表: ${report.name}`);
};
</script>

<template>
  <div class="p-6">
    <!-- Header -->
    <div class="mb-6">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h1 :class="['text-2xl font-medium mb-2', textPrimary]">报表中心</h1>
          <p :class="['text-sm', textSecondary]">管理和查看所有业务报表</p>
        </div>
        <button class="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 rounded-lg transition-all text-white">
          <el-icon :size="18"><Plus /></el-icon>
          <span>创建报表</span>
        </button>
      </div>

      <!-- Filters and Search -->
      <div class="flex flex-col sm:flex-row gap-4">
        <!-- Category Filter -->
        <div class="flex items-center gap-2 flex-wrap">
          <el-icon :size="18" :class="textSecondary"><Filter /></el-icon>
          <button
            v-for="category in categories"
            :key="category"
            @click="selectedCategory = category"
            :class="[
              'px-4 py-2 rounded-lg text-sm transition-all border',
              selectedCategory === category
                ? 'bg-cyan-500/20 text-cyan-600 border-cyan-500/30'
                : theme === 'dark'
                ? 'bg-slate-800/50 text-slate-400 border-slate-700 hover:text-white hover:border-slate-600'
                : 'bg-white text-slate-600 border-slate-200 hover:text-slate-900 hover:border-slate-300'
            ]"
          >
            {{ category }}
          </button>
        </div>

        <!-- Search -->
        <div class="relative sm:ml-auto">
          <el-icon :size="18" :class="['absolute left-3 top-1/2 -translate-y-1/2', theme === 'dark' ? 'text-slate-500' : 'text-slate-400']"><Search /></el-icon>
          <input
            v-model="searchTerm"
            type="text"
            placeholder="搜索报表..."
            :class="[
              'w-full sm:w-64 pl-10 pr-4 py-2 border rounded-lg text-sm placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50',
              inputBg,
              textPrimary
            ]"
          />
        </div>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <div :class="['rounded-xl border p-4', cardBg]">
        <div class="flex items-center justify-between">
          <div>
            <p :class="['text-sm mb-1', textSecondary]">总报表数</p>
            <p :class="['text-2xl font-bold', textPrimary]">156</p>
          </div>
          <div class="w-12 h-12 rounded-lg bg-cyan-500/20 flex items-center justify-center">
            <el-icon :size="24" class="text-cyan-500"><Document /></el-icon>
          </div>
        </div>
      </div>
      <div :class="['rounded-xl border p-4', cardBg]">
        <div class="flex items-center justify-between">
          <div>
            <p :class="['text-sm mb-1', textSecondary]">本月生成</p>
            <p :class="['text-2xl font-bold', textPrimary]">23</p>
          </div>
          <div class="w-12 h-12 rounded-lg bg-green-500/20 flex items-center justify-center">
            <el-icon :size="24" class="text-green-500"><Plus /></el-icon>
          </div>
        </div>
      </div>
      <div :class="['rounded-xl border p-4', cardBg]">
        <div class="flex items-center justify-between">
          <div>
            <p :class="['text-sm mb-1', textSecondary]">总下载量</p>
            <p :class="['text-2xl font-bold', textPrimary]">1,247</p>
          </div>
          <div class="w-12 h-12 rounded-lg bg-blue-500/20 flex items-center justify-center">
            <el-icon :size="24" class="text-blue-500"><Download /></el-icon>
          </div>
        </div>
      </div>
      <div :class="['rounded-xl border p-4', cardBg]">
        <div class="flex items-center justify-between">
          <div>
            <p :class="['text-sm mb-1', textSecondary]">预约报表</p>
            <p :class="['text-2xl font-bold', textPrimary]">8</p>
          </div>
          <div class="w-12 h-12 rounded-lg bg-purple-500/20 flex items-center justify-center">
            <el-icon :size="24" class="text-purple-500"><Calendar /></el-icon>
          </div>
        </div>
      </div>
    </div>

    <!-- Reports Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      <div
        v-for="report in filteredReports"
        :key="report.id"
        :class="[
          'rounded-xl border p-5 transition-all group',
          cardBg,
          theme === 'dark' ? 'hover:border-cyan-500/30' : 'hover:border-cyan-300'
        ]"
      >
        <!-- Icon and Status -->
        <div class="flex items-start justify-between mb-4">
          <div class="w-12 h-12 rounded-lg bg-gradient-to-br from-cyan-500/20 to-blue-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
            <el-icon :size="24" class="text-cyan-500"><Document /></el-icon>
          </div>
          <span :class="['inline-flex items-center px-3 py-1 rounded-full text-xs border', getStatusBadge(report.status).class]">
            {{ getStatusBadge(report.status).text }}
          </span>
        </div>

        <!-- Report Info -->
        <h3 :class="['text-sm font-medium mb-2 line-clamp-2 group-hover:text-cyan-500 transition-colors', textPrimary]">
          {{ report.name }}
        </h3>
        <p :class="['text-xs mb-4', textSecondary]">{{ report.category }}</p>

        <!-- Meta Info -->
        <div :class="['flex items-center justify-between text-xs mb-4', theme === 'dark' ? 'text-slate-500' : 'text-slate-400']">
          <div class="flex items-center gap-1">
            <el-icon :size="12"><Calendar /></el-icon>
            <span>{{ report.createDate }}</span>
          </div>
          <span>{{ report.size }}</span>
        </div>

        <!-- Actions -->
        <div class="flex gap-2">
          <button
            :disabled="report.status !== 'completed'"
            @click="handlePreview(report)"
            :class="[
              'flex-1 flex items-center justify-center gap-1 px-3 py-2 rounded-lg text-xs transition-all disabled:opacity-50 disabled:cursor-not-allowed',
              theme === 'dark' ? 'bg-slate-800 hover:bg-slate-700' : 'bg-slate-100 hover:bg-slate-200'
            ]"
          >
            <el-icon :size="14"><View /></el-icon>
            <span>预览</span>
          </button>
          <button
            :disabled="report.status !== 'completed'"
            @click="handleDownload(report)"
            class="flex-1 flex items-center justify-center gap-1 px-3 py-2 bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-600 rounded-lg text-xs transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <el-icon :size="14"><Download /></el-icon>
            <span>下载</span>
          </button>
        </div>

        <!-- Download Count -->
        <p v-if="report.downloads > 0" :class="['text-xs mt-3 text-center', theme === 'dark' ? 'text-slate-500' : 'text-slate-400']">
          已下载 {{ report.downloads }} 次
        </p>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredReports.length === 0" class="text-center py-16">
      <div :class="['w-16 h-16 rounded-full mx-auto mb-4 flex items-center justify-center', theme === 'dark' ? 'bg-slate-800' : 'bg-slate-200']">
        <el-icon :size="32" :class="theme === 'dark' ? 'text-slate-600' : 'text-slate-400'"><Document /></el-icon>
      </div>
      <h3 :class="['text-lg font-medium mb-2', textPrimary]">暂无报表</h3>
      <p :class="['text-sm', textSecondary]">未找到符合条件的报表</p>
    </div>

    <!-- Report Preview Modal -->
    <Teleport to="body">
      <div v-if="previewReport" class="fixed inset-0 z-50 flex items-center justify-center p-4" :class="theme === 'dark' ? 'bg-black/70' : 'bg-black/50'">
        <div :class="['rounded-2xl shadow-2xl w-full max-w-6xl max-h-[90vh] overflow-hidden flex flex-col', modalBg]">
          <!-- Modal Header -->
          <div :class="['flex items-center justify-between p-6 border-b', borderClass]">
            <div>
              <h2 :class="['text-xl font-medium', textPrimary]">{{ previewReport.name }}</h2>
              <p :class="['text-sm mt-1', textSecondary]">{{ previewReport.category }} · {{ previewReport.createDate }}</p>
            </div>
            <div class="flex items-center gap-2">
              <button
                @click="toggleChat"
                :class="[
                  'flex items-center gap-2 px-4 py-2 rounded-lg transition-all',
                  showChat ? 'bg-cyan-500 text-white' : 'bg-cyan-500/20 text-cyan-600 hover:bg-cyan-500/30'
                ]"
              >
                <el-icon :size="18"><ChatDotRound /></el-icon>
                <span>{{ showChat ? 'AI分析中' : '开启AI分析' }}</span>
              </button>
              <button class="flex items-center gap-2 px-4 py-2 bg-green-500/20 text-green-600 hover:bg-green-500/30 rounded-lg transition-all">
                <el-icon :size="18"><Download /></el-icon>
                <span>下载</span>
              </button>
              <button
                @click="closePreview"
                :class="[
                  'p-2 rounded-lg transition-colors',
                  theme === 'dark' ? 'hover:bg-slate-700 text-slate-400' : 'hover:bg-slate-100 text-slate-600'
                ]"
              >
                <el-icon :size="20"><Close /></el-icon>
              </button>
            </div>
          </div>

          <!-- Modal Content -->
          <div class="flex-1 overflow-hidden flex">
            <!-- Report Content -->
            <div :class="['flex-1 overflow-y-auto p-6', showChat ? 'border-r ' + borderClass : '']">
              <!-- Summary -->
              <div :class="['border rounded-xl p-6 mb-6', modalCardBg]">
                <h3 :class="['text-lg font-medium mb-3', textPrimary]">报表摘要</h3>
                <p :class="['text-sm leading-relaxed', textSecondary]">{{ previewReport.data?.summary || '暂无摘要数据' }}</p>
              </div>

              <!-- Charts -->
              <div v-if="previewReport.data?.charts" :class="['border rounded-xl p-6 mb-6', modalCardBg]">
                <h3 :class="['text-lg font-medium mb-4', textPrimary]">核心指标</h3>
                <div class="grid grid-cols-2 gap-4">
                  <div v-for="(chart, index) in previewReport.data.charts" :key="index" :class="['p-4 rounded-lg', theme === 'dark' ? 'bg-slate-700/30' : 'bg-white']">
                    <div class="flex items-center gap-2 mb-2">
                      <el-icon :size="16" class="text-cyan-500"><DataAnalysis /></el-icon>
                      <span :class="['text-xs', textSecondary]">{{ getChartLabel(chart.type) }}</span>
                    </div>
                    <div :class="['text-2xl font-bold mb-1', textPrimary]">{{ formatChartValue(chart) }}</div>
                    <span :class="['text-xs', chart.growth >= 0 ? 'text-green-500' : 'text-red-500']">{{ chart.growth >= 0 ? '+' : '' }}{{ chart.growth }}%</span>
                  </div>
                </div>
              </div>

              <!-- Top Products -->
              <div v-if="previewReport.data?.topProducts" :class="['border rounded-xl p-6 mb-6', modalCardBg]">
                <h3 :class="['text-lg font-medium mb-4', textPrimary]">热销商品</h3>
                <div class="space-y-3">
                  <div v-for="(product, index) in previewReport.data.topProducts" :key="index" :class="['flex items-center justify-between p-3 rounded-lg', theme === 'dark' ? 'bg-slate-700/30' : 'bg-white']">
                    <div>
                      <p :class="['text-sm font-medium', textPrimary]">{{ product.name }}</p>
                      <p :class="['text-xs', textSecondary]">销量: {{ product.sales }}</p>
                    </div>
                    <span class="text-sm text-cyan-500 font-medium">￥{{ product.amount.toLocaleString() }}</span>
                  </div>
                </div>
              </div>

              <!-- Alerts -->
              <div v-if="previewReport.data?.alerts" :class="['border rounded-xl p-6 mb-6', modalCardBg]">
                <h3 :class="['text-lg font-medium mb-4', textPrimary]">预警信息</h3>
                <div class="space-y-3">
                  <div v-for="(alert, index) in previewReport.data.alerts" :key="index" class="flex items-center justify-between p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
                    <div>
                      <p :class="['text-sm font-medium', textPrimary]">{{ alert.product }}</p>
                      <p :class="['text-xs', textSecondary]">当前库存: {{ alert.stock }}</p>
                    </div>
                    <span class="text-xs text-red-500 px-2 py-1 bg-red-500/20 rounded">{{ alert.status }}</span>
                  </div>
                </div>
              </div>

              <!-- Suppliers -->
              <div v-if="previewReport.data?.suppliers" :class="['border rounded-xl p-6 mb-6', modalCardBg]">
                <h3 :class="['text-lg font-medium mb-4', textPrimary]">主要供应商</h3>
                <div class="space-y-3">
                  <div v-for="(supplier, index) in previewReport.data.suppliers" :key="index" :class="['flex items-center justify-between p-3 rounded-lg', theme === 'dark' ? 'bg-slate-700/30' : 'bg-white']">
                    <div>
                      <p :class="['text-sm font-medium', textPrimary]">{{ supplier.name }}</p>
                      <p :class="['text-xs', textSecondary]">订单数: {{ supplier.orders }}</p>
                    </div>
                    <span class="text-sm text-cyan-500 font-medium">￥{{ supplier.amount.toLocaleString() }}</span>
                  </div>
                </div>
              </div>

              <!-- Customers -->
              <div v-if="previewReport.data?.customers" :class="['border rounded-xl p-6', modalCardBg]">
                <h3 :class="['text-lg font-medium mb-4', textPrimary]">重点客户</h3>
                <div class="space-y-3">
                  <div v-for="(customer, index) in previewReport.data.customers" :key="index" :class="['flex items-center justify-between p-3 rounded-lg', theme === 'dark' ? 'bg-slate-700/30' : 'bg-white']">
                    <div>
                      <div class="flex items-center gap-2">
                        <p :class="['text-sm font-medium', textPrimary]">{{ customer.name }}</p>
                        <span v-if="customer.level === 'VIP'" class="text-xs px-2 py-0.5 bg-yellow-500/20 text-yellow-600 border border-yellow-500/30 rounded">VIP</span>
                      </div>
                    </div>
                    <span class="text-sm text-cyan-500 font-medium">￥{{ customer.amount.toLocaleString() }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- AI Chat Panel -->
            <div v-if="showChat" class="w-96 flex flex-col">
              <!-- Chat Header -->
              <div :class="['p-4 border-b', borderClass]">
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
                    <el-icon :size="20" class="text-white"><ChatDotRound /></el-icon>
                  </div>
                  <div>
                    <h3 :class="['text-sm font-medium', textPrimary]">AI智能分析</h3>
                    <p :class="['text-xs', textSecondary]">实时对话分析</p>
                  </div>
                </div>
              </div>

              <!-- Messages -->
              <div ref="messagesContainer" class="flex-1 overflow-y-auto p-4 space-y-4">
                <!-- Suggested Questions -->
                <div v-if="messages.length === 1" class="space-y-2 mb-4">
                  <p :class="['text-xs', textSecondary]">快速提问：</p>
                  <button
                    v-for="(q, index) in suggestedQuestions"
                    :key="index"
                    @click="handleQuickQuestion(q)"
                    :class="[
                      'w-full text-left px-3 py-2 text-xs rounded-lg transition-all',
                      theme === 'dark' ? 'bg-slate-700/50 hover:bg-slate-700 text-slate-300' : 'bg-slate-100 hover:bg-slate-200 text-slate-700'
                    ]"
                  >
                    {{ q }}
                  </button>
                </div>

                <!-- Message List -->
                <div v-for="message in messages" :key="message.id" :class="['flex gap-3', message.type === 'user' ? 'flex-row-reverse' : '']">
                  <div :class="[
                    'w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center',
                    message.type === 'ai' ? 'bg-gradient-to-br from-cyan-500 to-blue-600' : 'bg-gradient-to-br from-purple-500 to-pink-600'
                  ]">
                    <el-icon v-if="message.type === 'ai'" :size="14" class="text-white"><ChatDotRound /></el-icon>
                    <span v-else class="text-xs text-white">李</span>
                  </div>
                  <div :class="['flex-1', message.type === 'user' ? 'flex justify-end' : '']">
                    <div :class="[
                      'text-xs p-3 rounded-lg max-w-[85%]',
                      message.type === 'ai'
                        ? theme === 'dark' ? 'bg-slate-700 text-slate-100' : 'bg-slate-100 text-slate-900'
                        : 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white'
                    ]">
                      <p class="whitespace-pre-wrap leading-relaxed">{{ message.content }}</p>
                      <p :class="['text-xs mt-1', message.type === 'ai' ? 'text-slate-500' : 'text-cyan-100']">
                        {{ formatTime(message.timestamp) }}
                      </p>
                    </div>
                  </div>
                </div>

                <!-- Typing Indicator -->
                <div v-if="isTyping" class="flex gap-3">
                  <div class="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
                    <el-icon :size="14" class="text-white"><ChatDotRound /></el-icon>
                  </div>
                  <div :class="['px-3 py-2 rounded-lg', theme === 'dark' ? 'bg-slate-700' : 'bg-slate-100']">
                    <div class="flex gap-1">
                      <div class="w-2 h-2 bg-slate-500 rounded-full animate-bounce"></div>
                      <div class="w-2 h-2 bg-slate-500 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                      <div class="w-2 h-2 bg-slate-500 rounded-full animate-bounce" style="animation-delay: 0.4s"></div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Input -->
              <div :class="['p-4 border-t', borderClass]">
                <div class="flex gap-2">
                  <input
                    v-model="inputValue"
                    type="text"
                    placeholder="输入您的问题..."
                    @keypress.enter="handleSendMessage"
                    :class="[
                      'flex-1 px-3 py-2 text-sm rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500/50',
                      theme === 'dark' ? 'bg-slate-700 text-white placeholder-slate-400' : 'bg-slate-100 text-slate-900 placeholder-slate-500'
                    ]"
                  />
                  <button
                    @click="handleSendMessage"
                    :disabled="!inputValue.trim()"
                    class="px-3 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <el-icon :size="16" class="text-white"><Promotion /></el-icon>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
