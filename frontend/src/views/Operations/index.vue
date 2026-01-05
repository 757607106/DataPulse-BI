<template>
  <div class="operations-container" :class="themeClass">
    <div class="operations-header">
      <h2 :class="['text-2xl font-bold', textPrimary]">智能操作中心</h2>
      <p :class="['text-sm mt-1', textSecondary]">支持 AI 智能指令和手动录入两种方式</p>
    </div>

    <el-tabs v-model="activeTab" class="operations-tabs">
      <!-- Tab 1: AI 智能指令 -->
      <el-tab-pane label="✨ AI 智能指令" name="ai">
        <div class="ai-command-panel">
          <!-- 输入区域 -->
          <div class="command-input-section">
            <el-input
              v-model="aiCommand"
              type="textarea"
              :rows="4"
              placeholder="请输入自然语言指令，例如：
- 从总仓发货 50 个 iPhone 给京东
- 采购 100 台笔记本电脑入库到北京仓
- 销售 20 部小米手机给天猫"
              class="command-textarea"
            />
            <el-button
              type="primary"
              :loading="parsing"
              :disabled="!aiCommand.trim()"
              class="parse-button"
              @click="handleParseCommand"
            >
              <span v-if="!parsing">✨ AI 解析</span>
              <span v-else>解析中...</span>
            </el-button>
          </div>

          <!-- AI 解析结果卡片 -->
          <transition name="fade-slide">
            <div v-if="parseResult" class="result-card">
              <div class="result-header">
                <h3 :class="['text-lg font-semibold', textPrimary]">AI 解析结果</h3>
                <el-tag :type="parseResult.confidence >= 0.8 ? 'success' : 'warning'">
                  置信度: {{ (parseResult.confidence * 100).toFixed(0) }}%
                </el-tag>
              </div>

              <div class="result-content">
                <el-descriptions :column="2" border>
                  <el-descriptions-item label="操作类型">
                    <el-tag :type="parseResult.operation_type === 'inbound' ? 'success' : 'primary'">
                      {{ parseResult.operation_type === 'inbound' ? '采购入库' : '销售出库' }}
                    </el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="AI 说明">
                    {{ parseResult.explanation }}
                  </el-descriptions-item>
                </el-descriptions>

                <div class="items-table mt-4">
                  <h4 :class="['text-sm font-medium mb-2', textSecondary]">商品明细</h4>
                  <el-table :data="parseResult.items" border style="width: 100%">
                    <el-table-column prop="product_id" label="商品ID" width="100" />
                    <el-table-column prop="quantity" label="数量" width="100" />
                    <el-table-column prop="price" label="单价" width="120">
                      <template #default="{ row }">
                        ¥{{ row.price.toFixed(2) }}
                      </template>
                    </el-table-column>
                    <el-table-column label="小计">
                      <template #default="{ row }">
                        ¥{{ (row.quantity * row.price).toFixed(2) }}
                      </template>
                    </el-table-column>
                  </el-table>
                </div>

                <div class="total-amount mt-3">
                  <span :class="textSecondary">总金额：</span>
                  <span class="text-2xl font-bold" :class="amountClass">
                    ¥{{ calculateTotal(parseResult.items).toFixed(2) }}
                  </span>
                </div>
              </div>

              <div class="result-actions">
                <el-button @click="parseResult = null">❌ 取消</el-button>
                <el-button
                  type="primary"
                  :loading="executing"
                  @click="handleConfirmExecution"
                >
                  ✅ 确认执行
                </el-button>
              </div>
            </div>
          </transition>
        </div>
      </el-tab-pane>

      <!-- Tab 2: 手动录入 -->
      <el-tab-pane label="📝 手动录入" name="manual">
        <div class="manual-entry-panel">
          <el-form
            ref="manualFormRef"
            :model="manualForm"
            :rules="manualRules"
            label-width="120px"
            class="manual-form"
          >
            <!-- 操作类型 -->
            <el-form-item label="操作类型" prop="operationType">
              <el-radio-group v-model="manualForm.operationType" @change="handleOperationTypeChange">
                <el-radio-button label="inbound">采购入库</el-radio-button>
                <el-radio-button label="outbound">销售出库</el-radio-button>
              </el-radio-group>
            </el-form-item>

            <!-- 合作伙伴（供应商/客户） -->
            <el-form-item
              :label="manualForm.operationType === 'inbound' ? '供应商' : '客户'"
              prop="partnerId"
            >
              <el-select
                v-model="manualForm.partnerId"
                placeholder="请选择"
                filterable
                style="width: 100%"
              >
                <el-option
                  v-for="partner in partnerList"
                  :key="partner.id"
                  :label="partner.name"
                  :value="partner.id"
                />
              </el-select>
            </el-form-item>

            <!-- 仓库 -->
            <el-form-item label="仓库" prop="warehouseId">
              <el-select
                v-model="manualForm.warehouseId"
                placeholder="请选择仓库"
                filterable
                style="width: 100%"
              >
                <el-option
                  v-for="warehouse in warehouseList"
                  :key="warehouse.id"
                  :label="warehouse.name"
                  :value="warehouse.id"
                />
              </el-select>
            </el-form-item>

            <!-- 业务员 -->
            <el-form-item label="业务员" prop="salesmanId">
              <el-select
                v-model="manualForm.salesmanId"
                placeholder="请选择业务员"
                filterable
                style="width: 100%"
              >
                <el-option
                  v-for="salesman in salesmanList"
                  :key="salesman.id"
                  :label="salesman.name"
                  :value="salesman.id"
                />
              </el-select>
            </el-form-item>

            <!-- 商品明细 -->
            <el-form-item label="商品明细">
              <div class="items-editor">
                <el-button type="primary" size="small" @click="handleAddItem">
                  + 添加商品
                </el-button>

                <div v-for="(item, index) in manualForm.items" :key="index" class="item-row">
                  <el-select
                    v-model="item.product_id"
                    placeholder="选择商品"
                    filterable
                    style="width: 300px"
                  >
                    <el-option
                      v-for="product in productList"
                      :key="product.id"
                      :label="`${product.name} (${product.category})`"
                      :value="product.id"
                    />
                  </el-select>

                  <el-input-number
                    v-model="item.quantity"
                    :min="1"
                    :precision="2"
                    placeholder="数量"
                    style="width: 150px"
                  />

                  <el-input-number
                    v-model="item.price"
                    :min="0.01"
                    :precision="2"
                    placeholder="单价"
                    style="width: 150px"
                  />

                  <span class="item-subtotal">
                    小计: ¥{{ ((item.quantity || 0) * (item.price || 0)).toFixed(2) }}
                  </span>

                  <el-button
                    type="danger"
                    size="small"
                    text
                    @click="handleRemoveItem(index)"
                  >
                    删除
                  </el-button>
                </div>

                <div v-if="manualForm.items.length > 0" class="manual-total">
                  <span class="text-gray-400">总金额：</span>
                  <span class="text-2xl font-bold text-blue-400">
                    ¥{{ calculateManualTotal().toFixed(2) }}
                  </span>
                </div>
              </div>
            </el-form-item>

            <!-- 备注 -->
            <el-form-item label="备注">
              <el-input
                v-model="manualForm.remark"
                type="textarea"
                :rows="2"
                placeholder="选填"
              />
            </el-form-item>

            <!-- 提交按钮 -->
            <el-form-item>
              <el-button
                type="primary"
                :loading="submitting"
                :disabled="manualForm.items.length === 0"
                @click="handleManualSubmit"
              >
                提交单据
              </el-button>
              <el-button @click="handleResetManualForm">重置</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import { useThemeStore } from '@/stores/theme';
import { ElMessage, ElMessageBox } from 'element-plus';
import type { FormInstance, FormRules } from 'element-plus';
import {
  parseCommand,
  inbound,
  outbound,
  getProducts,
  getWarehouses,
  getPartners,
  getSalesmen,
  type ParseCommandResult,
  type OrderItem,
  type Product,
  type Warehouse,
  type Partner,
  type Salesman,
} from '@/api/business';

defineOptions({
  name: 'OperationsPage'
});

// Tab 状态
const activeTab = ref('ai');

// 主题
const themeStore = useThemeStore();
const theme = computed(() => themeStore.theme);
const themeClass = computed(() => (theme.value === 'dark' ? 'theme-dark' : 'theme-light'));
const textPrimary = computed(() => (theme.value === 'dark' ? 'text-white' : 'text-[#0F172A]'));
const textSecondary = computed(() => (theme.value === 'dark' ? 'text-gray-300' : 'text-gray-600'));
const amountClass = computed(() => (theme.value === 'dark' ? 'text-blue-400' : 'text-blue-600'));

// ========== AI 智能指令 ==========
const aiCommand = ref('');
const parsing = ref(false);
const executing = ref(false);
const parseResult = ref<ParseCommandResult | null>(null);

/**
 * AI 解析指令
 */
const handleParseCommand = async () => {
  if (!aiCommand.value.trim()) {
    ElMessage.warning('请输入指令');
    return;
  }

  parsing.value = true;
  try {
    const result = await parseCommand({ command: aiCommand.value });
    parseResult.value = result;

    if (result.confidence < 0.6) {
      ElMessage.warning('AI 解析置信度较低，请检查指令是否清晰');
    }
  } catch (error: any) {
    console.error('AI 解析失败:', error);
    ElMessage.error(error.response?.data?.detail || 'AI 解析失败');
  } finally {
    parsing.value = false;
  }
};

/**
 * 确认执行 AI 解析的指令
 */
const handleConfirmExecution = async () => {
  if (!parseResult.value) return;

  try {
    await ElMessageBox.confirm(
      `确认执行${parseResult.value.operation_type === 'inbound' ? '采购入库' : '销售出库'}操作吗？`,
      '确认',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );

    executing.value = true;

    // 构造请求数据
    const requestData = {
      warehouse_id: parseResult.value.warehouse_id!,
      salesman_id: parseResult.value.salesman_id!,
      items: parseResult.value.items,
      remark: parseResult.value.remark,
    };

    let response;
    if (parseResult.value.operation_type === 'inbound') {
      response = await inbound({
        ...requestData,
        supplier_id: parseResult.value.partner_id!,
      });
    } else {
      response = await outbound({
        ...requestData,
        customer_id: parseResult.value.partner_id!,
      });
    }

    ElMessage.success(response.message);
    
    // 清空表单
    aiCommand.value = '';
    parseResult.value = null;
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('执行失败:', error);
      ElMessage.error(error.response?.data?.detail || '操作失败');
    }
  } finally {
    executing.value = false;
  }
};

/**
 * 计算总金额
 */
const calculateTotal = (items: OrderItem[]) => {
  return items.reduce((sum, item) => sum + item.quantity * item.price, 0);
};

// ========== 手动录入 ==========
const manualFormRef = ref<FormInstance>();
const submitting = ref(false);

// 下拉列表数据
const productList = ref<Product[]>([]);
const warehouseList = ref<Warehouse[]>([]);
const partnerList = ref<Partner[]>([]);
const salesmanList = ref<Salesman[]>([]);

// 手动表单数据
const manualForm = reactive({
  operationType: 'inbound' as 'inbound' | 'outbound',
  partnerId: null as number | null,
  warehouseId: null as number | null,
  salesmanId: null as number | null,
  items: [] as OrderItem[],
  remark: '',
});

// 表单验证规则
const manualRules: FormRules = {
  operationType: [{ required: true, message: '请选择操作类型', trigger: 'change' }],
  partnerId: [{ required: true, message: '请选择合作伙伴', trigger: 'change' }],
  warehouseId: [{ required: true, message: '请选择仓库', trigger: 'change' }],
  salesmanId: [{ required: true, message: '请选择业务员', trigger: 'change' }],
};

/**
 * 操作类型切换
 */
const handleOperationTypeChange = async (type: 'inbound' | 'outbound') => {
  manualForm.partnerId = null;
  await loadPartners(type);
};

/**
 * 添加商品明细
 */
const handleAddItem = () => {
  manualForm.items.push({
    product_id: 0,
    quantity: 1,
    price: 0,
  });
};

/**
 * 删除商品明细
 */
const handleRemoveItem = (index: number) => {
  manualForm.items.splice(index, 1);
};

/**
 * 计算手动录入的总金额
 */
const calculateManualTotal = () => {
  return manualForm.items.reduce((sum, item) => {
    return sum + (item.quantity || 0) * (item.price || 0);
  }, 0);
};

/**
 * 手动提交
 */
const handleManualSubmit = async () => {
  if (!manualFormRef.value) return;

  try {
    await manualFormRef.value.validate();

    if (manualForm.items.length === 0) {
      ElMessage.warning('请至少添加一个商品');
      return;
    }

    // 验证商品明细
    for (const item of manualForm.items) {
      if (!item.product_id || item.product_id === 0) {
        ElMessage.warning('请选择商品');
        return;
      }
      if (!item.quantity || item.quantity <= 0) {
        ElMessage.warning('请输入正确的数量');
        return;
      }
      if (!item.price || item.price <= 0) {
        ElMessage.warning('请输入正确的单价');
        return;
      }
    }

    submitting.value = true;

    const requestData = {
      warehouse_id: manualForm.warehouseId!,
      salesman_id: manualForm.salesmanId!,
      items: manualForm.items,
      remark: manualForm.remark || undefined,
    };

    let response;
    if (manualForm.operationType === 'inbound') {
      response = await inbound({
        ...requestData,
        supplier_id: manualForm.partnerId!,
      });
    } else {
      response = await outbound({
        ...requestData,
        customer_id: manualForm.partnerId!,
      });
    }

    ElMessage.success(response.message);
    handleResetManualForm();
  } catch (error: any) {
    console.error('提交失败:', error);
    ElMessage.error(error.response?.data?.detail || '操作失败');
  } finally {
    submitting.value = false;
  }
};

/**
 * 重置手动表单
 */
const handleResetManualForm = () => {
  manualFormRef.value?.resetFields();
  manualForm.items = [];
};

/**
 * 加载商品列表
 */
const loadProducts = async () => {
  try {
    productList.value = await getProducts();
  } catch (error) {
    console.error('加载商品列表失败:', error);
  }
};

/**
 * 加载仓库列表
 */
const loadWarehouses = async () => {
  try {
    warehouseList.value = await getWarehouses();
  } catch (error) {
    console.error('加载仓库列表失败:', error);
  }
};

/**
 * 加载合作伙伴列表
 */
const loadPartners = async (type: 'inbound' | 'outbound') => {
  try {
    const partnerType = type === 'inbound' ? 'supplier' : 'customer';
    partnerList.value = await getPartners(partnerType);
  } catch (error) {
    console.error('加载合作伙伴列表失败:', error);
  }
};

/**
 * 加载业务员列表
 */
const loadSalesmen = async () => {
  try {
    salesmanList.value = await getSalesmen();
  } catch (error) {
    console.error('加载业务员列表失败:', error);
  }
};

// 页面初始化
onMounted(() => {
  loadProducts();
  loadWarehouses();
  loadPartners('inbound');
  loadSalesmen();
});
</script>

<style scoped lang="scss">
.operations-container {
  padding: 24px;
}

.operations-header {
  margin-bottom: 24px;
}

.operations-tabs {
  :deep(.el-tabs__header) {
    background: rgba(30, 41, 59, 0.6);
    border-radius: 8px 8px 0 0;
    padding: 0 16px;
    margin-bottom: 0;
  }

  :deep(.el-tabs__content) {
    background: rgba(30, 41, 59, 0.4);
    border-radius: 0 0 8px 8px;
    padding: 24px;
    min-height: 500px;
  }
}

/* Light theme overrides */
.operations-container.theme-light {
  color: #0F172A;
}
.operations-container.theme-light .operations-tabs :deep(.el-tabs__header) {
  background: #F3F4F6;
}
.operations-container.theme-light .operations-tabs :deep(.el-tabs__content) {
  background: #FFFFFF;
}
.operations-container.theme-light .command-textarea :deep(.el-textarea__inner) {
  background: #FFFFFF;
  border-color: #E5E7EB;
  color: #0F172A;
}
.operations-container.theme-light :deep(.el-textarea__inner) {
  background: #FFFFFF !important;
  border-color: #E5E7EB !important;
  color: #0F172A !important;
}
.operations-container.theme-light .result-card {
  background: #FFFFFF;
  border: 1px solid rgba(14,165,233,0.06);
}
.operations-container.theme-light .total-amount {
  background: rgba(59, 130, 246, 0.04);
}
.operations-container.theme-light .manual-total {
  background: rgba(59, 130, 246, 0.04);
}

// AI 智能指令样式
.ai-command-panel {
  .command-input-section {
    margin-bottom: 24px;

    .command-textarea {
      margin-bottom: 16px;

      :deep(.el-textarea__inner) {
        background: rgba(15, 23, 42, 0.6);
        border-color: rgba(148, 163, 184, 0.2);
        color: #e2e8f0;
        font-size: 14px;
      }
    }

    .parse-button {
      width: 100%;
      height: 48px;
      font-size: 16px;
      font-weight: 600;
    }
  }

  .result-card {
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid rgba(59, 130, 246, 0.3);
    border-radius: 8px;
    padding: 24px;

    .result-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
    }

    .result-content {
      margin-bottom: 24px;
    }

    .result-actions {
      display: flex;
      justify-content: flex-end;
      gap: 12px;
    }
  }

  .total-amount {
    text-align: right;
    padding: 16px;
    background: rgba(59, 130, 246, 0.1);
    border-radius: 4px;
  }
}

// 手动录入样式
.manual-entry-panel {
  .manual-form {
    max-width: 800px;
  }

  .items-editor {
    width: 100%;

    .item-row {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-top: 12px;

      .item-subtotal {
        color: #94a3b8;
        font-size: 14px;
        min-width: 120px;
      }
    }

    .manual-total {
      margin-top: 16px;
      padding: 16px;
      background: rgba(59, 130, 246, 0.1);
      border-radius: 4px;
      text-align: right;
    }
  }
}

// 动画
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(-20px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(20px);
}
</style>
