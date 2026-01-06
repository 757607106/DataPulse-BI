<script setup lang="ts">
import { ref, computed, nextTick } from 'vue';
import { useThemeStore } from '@/stores/theme';
import { Promotion, TrendCharts, PieChart, MagicStick, ChatDotRound, View, Document } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';
import { sendMessage } from '@/api/chat';
import type { ChatMessage, LOADING_STAGES } from '@/types/chat';
import { convertToEChartsOption } from '@/utils/chartAdapter';
import BaseChart from '@/components/Charts/BaseChart.vue';

defineOptions({
  name: 'AnalysisPage'
});

const themeStore = useThemeStore();
const theme = computed(() => themeStore.theme);

const suggestedQuestions = [
  { icon: TrendCharts, text: '本月销售趋势如何？', color: '#06B6D4' },
  { icon: PieChart, text: '各商品类别的销售占比？', color: '#10B981' },
  { icon: MagicStick, text: '哪些商品库存告急？', color: '#F59E0B' },
  { icon: ChatDotRound, text: '预测下季度销售额', color: '#8B5CF6' },
];

const messages = ref<ChatMessage[]>([
  {
    id: 1,
    type: 'ai',
    content: '您好！我是智能进销存分析助手，基于 Vanna 2.0 + 通义千问，可以帮您分析库存数据、生成销售报表、预测采购需求。请问有什么可以帮您的？',
    timestamp: new Date(),
  },
]);

const inputValue = ref('');
const messagesContainer = ref<HTMLElement | null>(null);

// 数据表格弹窗
const dataDialogVisible = ref(false);
const currentDataForDialog = ref<ChatMessage | null>(null);

// 样式计算
const bgClass = computed(() => theme.value === 'dark' ? 'bg-[#0F172A]' : 'bg-[#F8FAFC]');
const textPrimary = computed(() => theme.value === 'dark' ? 'text-white' : 'text-[#0F172A]');
const textSecondary = computed(() => theme.value === 'dark' ? 'text-slate-400' : 'text-slate-600');
const borderClass = computed(() => theme.value === 'dark' ? 'border-slate-800' : 'border-slate-200');
const cardBg = computed(() => theme.value === 'dark'
  ? 'bg-slate-800/50 border-slate-700'
  : 'bg-white border-slate-200 shadow-sm');
const inputBg = computed(() => theme.value === 'dark'
  ? 'bg-slate-800/50 border-slate-700'
  : 'bg-white border-slate-300');

const generateAIResponse = (question: string): string => {
  if (question.includes('销售')) {
    return '根据数据分析，本月总销售额为¥980,000，相比上月增长15.8%。主要增长来自电子产品类别，其中iPhone 15 Pro和联想笔记本电脑销售额比最高，分别达到¥881,902和¥779,844。';
  } else if (question.includes('库存')) {
    return '当前有15件商品库存预警，其中2件处于严重不足状态。建议优先补充：联想笔记本电脑（剩余45台，安全库存100台）、iPhone 15 Pro（剩余23台，安全库存50台）。A4打印纸库存156包，也需关注补货。';
  } else if (question.includes('预测')) {
    return '基于历史数据和季节性分析，预计下季度销售额将达到¥3,200,000，同比增长18%。建议提前备货热销商品：电子产品类（笔记本、手机）、办公用品类（A4纸、文具）。';
  } else if (question.includes('商品') || question.includes('类别')) {
    return '商品类别销售占比：电子产品45%、办公用品22%、家具家电18%、食品饮料10%、日用百货5%。电子产品保持领先地位，建议继续加大投入并优化库存结构。';
  } else if (question.includes('采购')) {
    return '本月共执行采购订单35笔，总采购额¥650,000。主要供应商：深圳科技有限公司（¥329,950，12笔订单）、上海办公用品批发（¥125,000，8笔订单）。到货准时率92%，建议与核心供应商建立长期合作关系。';
  } else if (question.includes('客户')) {
    return 'VIP客户贡献了68%的销售额。前三大客户：腾讯科技（¥269,970）、阿里巴巴（¥249,950）、字节跳动（¥47,910）。建议为VIP客户提供专属服务和优惠政策，提升客户粘性。';
  }
  return '感谢您的提问！我已经为您分析了相关数据。如需更详细的报表，可以前往"报表中心"查看完整分析。您也可以问我关于库存、销售、采购、客户等方面的问题。';
};

const scrollToBottom = async () => {
  await nextTick();
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
};

// 加载阶段描述
const getLoadingText = (stage?: ChatMessage['loadingStage']) => {
  if (!stage) return 'AI 正在思考...';
  const stages = {
    thinking: 'AI 正在思考...',
    generating: '生成 SQL 查询...',
    querying: '执行查询中...',
    done: '完成'
  };
  return stages[stage];
};

const handleSendMessage = async (text?: string) => {
  const messageText = text || inputValue.value;
  if (!messageText.trim()) return;

  // 添加用户消息
  const userMessage: ChatMessage = {
    id: Date.now(),
    type: 'user',
    content: messageText,
    timestamp: new Date(),
  };
  messages.value.push(userMessage);
  inputValue.value = '';
  scrollToBottom();

  // 添加 AI 加载消息
  const aiLoadingMessage: ChatMessage = {
    id: Date.now() + 1,
    type: 'ai',
    content: '',
    timestamp: new Date(),
    loading: true,
    loadingStage: 'thinking',
  };
  messages.value.push(aiLoadingMessage);
  scrollToBottom();

  try {
    // 模拟加载阶段
    setTimeout(() => {
      aiLoadingMessage.loadingStage = 'generating';
    }, 800);

    setTimeout(() => {
      aiLoadingMessage.loadingStage = 'querying';
    }, 1600);

    // 调用真实 API
    const response = await sendMessage({ question: messageText });

    // 移除加载消息
    const loadingIndex = messages.value.findIndex(m => m.id === aiLoadingMessage.id);
    if (loadingIndex !== -1) {
      messages.value.splice(loadingIndex, 1);
    }

    // 添加 AI 响应消息
    const aiMessage: ChatMessage = {
      id: Date.now() + 2,
      type: 'ai',
      content: response.answer_text,
      timestamp: new Date(),
      sql: response.sql,
      data: response.data,
      chartType: response.chart_type,
    };
    messages.value.push(aiMessage);
    scrollToBottom();
  } catch (error: any) {
    // 移除加载消息
    const loadingIndex = messages.value.findIndex(m => m.id === aiLoadingMessage.id);
    if (loadingIndex !== -1) {
      messages.value.splice(loadingIndex, 1);
    }

    // 显示错误消息
    const errorMessage: ChatMessage = {
      id: Date.now() + 2,
      type: 'ai',
      content: `抱歉，处理您的问题时出现错误：${error.response?.data?.detail || error.message || '未知错误'}。请稍后重试或换个问题试试。`,
      timestamp: new Date(),
    };
    messages.value.push(errorMessage);
    scrollToBottom();

    ElMessage.error('请求失败，请稍后重试');
  }
};

// 查看数据表格
const viewDataTable = (message: ChatMessage) => {
  currentDataForDialog.value = message;
  dataDialogVisible.value = true;
};

// 获取图表 Option
const getChartOption = (message: ChatMessage) => {
  if (!message.data || !message.chartType) return null;
  const isDark = theme.value === 'dark';
  return convertToEChartsOption(message.data, message.chartType, isDark);
};

const handleKeyPress = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    handleSendMessage();
  }
};

const formatTime = (date: Date) => {
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
};

const formatAnswerText = (text: string) => {
  // 简单的 Markdown 支持: 换行、加粗、代码
  return text
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/`(.*?)`/g, '<code class="px-1 py-0.5 bg-slate-700 rounded text-xs">$1</code>');
};
</script>

<template>
  <div :class="['h-full flex flex-col', bgClass]">
    <!-- Header -->
    <div :class="['p-6 border-b', borderClass]">
      <div class="flex items-center gap-3 mb-2">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
          <el-icon :size="20" class="text-white"><MagicStick /></el-icon>
        </div>
        <div>
          <h1 :class="['text-xl font-medium', textPrimary]">智能分析 ChatBI</h1>
          <p :class="['text-sm', textSecondary]">基于AI的进销存智能分析助手</p>
        </div>
      </div>
    </div>

    <!-- Messages Area -->
    <div ref="messagesContainer" class="flex-1 overflow-y-auto p-6">
      <div class="max-w-4xl mx-auto space-y-6">
        <!-- Suggested Questions (only show at start) -->
        <div v-if="messages.length === 1" class="mb-8">
          <p :class="['text-sm mb-4', textSecondary]">您可以问我：</p>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <button
              v-for="(q, index) in suggestedQuestions"
              :key="index"
              @click="handleSendMessage(q.text)"
              :class="[
                'flex items-center gap-3 p-4 border rounded-xl transition-all text-left group',
                cardBg,
                theme === 'dark' ? 'hover:border-cyan-500/50 hover:bg-slate-800' : 'hover:border-cyan-300 hover:shadow-md'
              ]"
            >
              <div
                class="w-10 h-10 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform"
                :style="{ backgroundColor: `${q.color}20` }"
              >
                <el-icon :size="20" :style="{ color: q.color }"><component :is="q.icon" /></el-icon>
              </div>
              <span :class="[
                'text-sm',
                textSecondary,
                theme === 'dark' ? 'group-hover:text-white' : 'group-hover:text-slate-900',
                'transition-colors'
              ]">
                {{ q.text }}
              </span>
            </button>
          </div>
        </div>

        <!-- Messages -->
        <div
          v-for="message in messages"
          :key="message.id"
          :class="['flex gap-4', message.type === 'user' ? 'flex-row-reverse' : '']"
        >
          <!-- Avatar -->
          <div
            :class="[
              'w-10 h-10 rounded-full flex-shrink-0 flex items-center justify-center',
              message.type === 'ai'
                ? 'bg-gradient-to-br from-cyan-500 to-blue-600'
                : 'bg-gradient-to-br from-purple-500 to-pink-600'
            ]"
          >
            <el-icon v-if="message.type === 'ai'" :size="18" class="text-white"><MagicStick /></el-icon>
            <span v-else class="text-sm text-white font-medium">李</span>
          </div>

          <!-- Message Content -->
          <div :class="['flex-1 max-w-2xl', message.type === 'user' ? 'flex justify-end' : '']">
            <!-- 加载状态 -->
            <div v-if="message.loading" :class="['border rounded-xl p-4', cardBg]">
              <div class="flex items-center gap-3">
                <div class="flex gap-2">
                  <div class="w-2 h-2 bg-cyan-500 rounded-full animate-bounce"></div>
                  <div class="w-2 h-2 bg-cyan-500 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                  <div class="w-2 h-2 bg-cyan-500 rounded-full animate-bounce" style="animation-delay: 0.4s"></div>
                </div>
                <span :class="['text-sm', textSecondary]">{{ getLoadingText(message.loadingStage) }}</span>
              </div>
            </div>

            <!-- 正常消息 -->
            <div
              v-else
              :class="[
                'rounded-xl p-4',
                message.type === 'ai'
                  ? theme === 'dark'
                    ? 'bg-slate-800/50 border border-slate-700'
                    : 'bg-white border border-slate-200 shadow-sm'
                  : 'bg-gradient-to-r from-cyan-600 to-blue-600'
              ]"
            >
              <!-- 文本内容 -->
              <div 
                :class="[
                  'text-sm leading-relaxed',
                  message.type === 'user' ? 'text-white' : textPrimary
                ]"
                v-html="formatAnswerText(message.content)"
              />

              <!-- SQL 折叠面板 -->
              <el-collapse v-if="message.sql" class="mt-4" accordion>
                <el-collapse-item name="sql">
                  <template #title>
                    <div :class="['flex items-center gap-2 text-xs', textSecondary]">
                      <el-icon :size="14"><Document /></el-icon>
                      <span>查看 SQL 查询</span>
                    </div>
                  </template>
                  <pre :class="[
                    'text-xs p-3 rounded-lg overflow-x-auto',
                    theme === 'dark' ? 'bg-slate-900 text-green-400' : 'bg-slate-50 text-slate-700'
                  ]">{{ message.sql }}</pre>
                </el-collapse-item>
              </el-collapse>

              <!-- 图表区域 -->
              <div
                v-if="message.data && message.chartType && message.chartType !== 'table'"
                :class="[
                  'mt-4 p-4 rounded-lg border',
                  theme === 'dark' ? 'bg-slate-900/50 border-slate-700' : 'bg-slate-50 border-slate-200'
                ]"
              >
                <div :class="['flex items-center justify-between mb-3']">
                  <div :class="['flex items-center gap-2 text-xs', textSecondary]">
                    <el-icon :size="14"><TrendCharts /></el-icon>
                    <span>数据可视化</span>
                  </div>
                  <el-button 
                    size="small" 
                    :icon="View" 
                    @click="viewDataTable(message)"
                    text
                  >
                    查看原始数据
                  </el-button>
                </div>
                <BaseChart 
                  :option="getChartOption(message)!"
                  height="300px"
                />
              </div>

              <!-- 表格类型直接显示按钮 -->
              <div
                v-if="message.data && message.chartType === 'table'"
                class="mt-4"
              >
                <el-button 
                  type="primary"
                  :icon="View" 
                  @click="viewDataTable(message)"
                  size="small"
                >
                  查看数据表格
                </el-button>
              </div>

              <p :class="[
                'text-xs mt-3',
                message.type === 'ai'
                  ? (theme === 'dark' ? 'text-slate-500' : 'text-slate-400')
                  : 'text-cyan-100'
              ]">
                {{ formatTime(message.timestamp) }}
              </p>
            </div>
          </div>
        </div>

        <!-- Typing Indicator - 已移除，由 loading 消息替代 -->
      </div>
    </div>

    <!-- Input Area -->
    <div :class="['p-6 border-t', borderClass]">
      <div class="max-w-4xl mx-auto">
        <div class="flex gap-3">
          <input
            v-model="inputValue"
            type="text"
            @keypress="handleKeyPress"
            placeholder="输入您的问题，例如：本月销售额是多少？"
            :class="[
              'flex-1 px-4 py-3 border rounded-xl text-sm placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50',
              inputBg,
              textPrimary
            ]"
          />
          <button
            @click="handleSendMessage()"
            :disabled="!inputValue.trim()"
            class="px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 text-white"
          >
            <el-icon :size="18"><Promotion /></el-icon>
            <span>发送</span>
          </button>
        </div>
        <p :class="['text-xs mt-3 text-center', theme === 'dark' ? 'text-slate-500' : 'text-slate-400']">
          提示：AI助手可能会产生不准确的信息，请以实际数据为准
        </p>
      </div>
    </div>

    <!-- 数据表格弹窗 -->
    <el-dialog
      v-model="dataDialogVisible"
      title="原始数据"
      width="80%"
      :append-to-body="true"
    >
      <el-table
        v-if="currentDataForDialog?.data"
        :data="currentDataForDialog.data.rows"
        stripe
        border
        max-height="500"
        style="width: 100%"
      >
        <el-table-column
          v-for="col in currentDataForDialog.data.columns"
          :key="col"
          :prop="col"
          :label="col"
          :min-width="120"
        />
      </el-table>
      <template #footer>
        <el-button @click="dataDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-4px);
  }
}
.animate-bounce {
  animation: bounce 0.6s infinite;
}
</style>
