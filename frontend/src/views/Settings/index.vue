<script setup lang="ts">
import { ref, computed } from 'vue';
import { User, Bell, Lock, Brush, FolderOpened, Setting, Check } from '@element-plus/icons-vue';

const theme = ref<'light' | 'dark'>('light');
const activeSection = ref('profile');

const settings = ref({
  // Profile
  username: '李仓管',
  email: 'licanguan@company.com',
  phone: '138****6666',
  department: '仓储部',
  position: '仓库管理员',
  
  // Notifications
  emailNotifications: true,
  pushNotifications: true,
  reportAlerts: true,
  systemUpdates: false,
  
  // Security
  twoFactorAuth: false,
  sessionTimeout: '30',
  
  // Appearance
  language: 'zh-CN',
  
  // Data
  autoBackup: true,
  backupFrequency: 'daily',
  dataRetention: '90',
});

const settingSections = [
  { id: 'profile', label: '个人资料', icon: User },
  { id: 'notifications', label: '通知设置', icon: Bell },
  { id: 'security', label: '安全与隐私', icon: Lock },
  { id: 'appearance', label: '外观设置', icon: Brush },
  { id: 'data', label: '数据管理', icon: FolderOpened },
  { id: 'system', label: '系统设置', icon: Setting },
];

// 样式计算
const bgClass = computed(() => theme.value === 'dark' ? 'bg-[#0F172A]' : 'bg-[#F8FAFC]');
const sidebarBg = computed(() => theme.value === 'dark' ? 'bg-gradient-to-b from-[#1E293B] to-[#0F172A]' : 'bg-white shadow-sm');
const borderClass = computed(() => theme.value === 'dark' ? 'border-slate-800' : 'border-slate-200');
const textPrimary = computed(() => theme.value === 'dark' ? 'text-white' : 'text-[#0F172A]');
const textSecondary = computed(() => theme.value === 'dark' ? 'text-slate-400' : 'text-slate-600');
const cardBg = computed(() => theme.value === 'dark' ? 'bg-slate-800/50 border-slate-700' : 'bg-white border-slate-200 shadow-sm');
const inputBg = computed(() => theme.value === 'dark' ? 'bg-slate-800/50 border-slate-700' : 'bg-slate-50 border-slate-300');

const handleSave = () => {
  alert('设置已保存！');
};

const toggleTheme = () => {
  theme.value = theme.value === 'dark' ? 'light' : 'dark';
};
</script>

<template>
  <div :class="['flex h-full', bgClass]">
    <!-- Settings Navigation -->
    <aside :class="['w-64 border-r p-6', borderClass, sidebarBg]">
      <h2 :class="['text-sm font-medium mb-4', textSecondary]">设置</h2>
      <nav class="space-y-1">
        <button
          v-for="section in settingSections"
          :key="section.id"
          @click="activeSection = section.id"
          :class="[
            'w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-all text-left',
            activeSection === section.id
              ? 'bg-cyan-500/20 text-cyan-500'
              : 'text-slate-400 hover:text-slate-900 hover:bg-slate-100'
          ]"
        >
          <el-icon :size="18"><component :is="section.icon" /></el-icon>
          <span>{{ section.label }}</span>
        </button>
      </nav>
    </aside>

    <!-- Settings Content -->
    <div :class="['flex-1 overflow-y-auto', bgClass]">
      <div class="max-w-3xl p-8">
        
        <!-- Profile Section -->
        <div v-if="activeSection === 'profile'" class="space-y-6">
          <div>
            <h2 :class="['text-xl font-medium mb-4', textPrimary]">个人资料</h2>
            <p :class="['text-sm mb-6', textSecondary]">管理您的个人信息和账户详情</p>
          </div>

          <!-- Avatar -->
          <div :class="['flex items-center gap-6 p-6 rounded-xl border', cardBg]">
            <div class="w-20 h-20 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center text-2xl text-white font-bold">
              李
            </div>
            <div>
              <button class="px-4 py-2 bg-cyan-500/20 text-cyan-600 border border-cyan-500/30 rounded-lg hover:bg-cyan-500/30 transition-all text-sm">
                更换头像
              </button>
              <p :class="['text-xs mt-2', textSecondary]">推荐尺寸：200x200像素</p>
            </div>
          </div>

          <!-- Form Fields -->
          <div class="space-y-4">
            <div>
              <label :class="['block text-sm mb-2', textSecondary]">用户名</label>
              <input
                v-model="settings.username"
                type="text"
                :class="['w-full px-4 py-2 border rounded-lg focus:outline-none focus:border-cyan-500/50', inputBg, textPrimary]"
              />
            </div>

            <div>
              <label :class="['block text-sm mb-2', textSecondary]">邮箱地址</label>
              <input
                v-model="settings.email"
                type="email"
                :class="['w-full px-4 py-2 border rounded-lg focus:outline-none focus:border-cyan-500/50', inputBg, textPrimary]"
              />
            </div>

            <div>
              <label :class="['block text-sm mb-2', textSecondary]">手机号码</label>
              <input
                v-model="settings.phone"
                type="tel"
                :class="['w-full px-4 py-2 border rounded-lg focus:outline-none focus:border-cyan-500/50', inputBg, textPrimary]"
              />
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label :class="['block text-sm mb-2', textSecondary]">部门</label>
                <input
                  v-model="settings.department"
                  type="text"
                  :class="['w-full px-4 py-2 border rounded-lg focus:outline-none focus:border-cyan-500/50', inputBg, textPrimary]"
                />
              </div>
              <div>
                <label :class="['block text-sm mb-2', textSecondary]">职位</label>
                <input
                  v-model="settings.position"
                  type="text"
                  :class="['w-full px-4 py-2 border rounded-lg focus:outline-none focus:border-cyan-500/50', inputBg, textPrimary]"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- Notifications Section -->
        <div v-else-if="activeSection === 'notifications'" class="space-y-6">
          <div>
            <h2 :class="['text-xl font-medium mb-4', textPrimary]">通知设置</h2>
            <p :class="['text-sm mb-6', textSecondary]">管理您接收通知的方式和频率</p>
          </div>

          <div class="space-y-4">
            <div
              v-for="item in [
                { key: 'emailNotifications', label: '邮件通知', desc: '接收重要事件的邮件提醒' },
                { key: 'pushNotifications', label: '推送通知', desc: '接收浏览器推送消息' },
                { key: 'reportAlerts', label: '报表提醒', desc: '报表生成完成时通知我' },
                { key: 'systemUpdates', label: '系统更新', desc: '系统维护和更新通知' },
              ]"
              :key="item.key"
              :class="['flex items-center justify-between p-4 rounded-xl border', cardBg]"
            >
              <div>
                <p :class="['text-sm font-medium mb-1', textPrimary]">{{ item.label }}</p>
                <p :class="['text-xs', textSecondary]">{{ item.desc }}</p>
              </div>
              <button
                @click="(settings as any)[item.key] = !(settings as any)[item.key]"
                :class="[
                  'relative w-12 h-6 rounded-full transition-colors',
                  (settings as any)[item.key] ? 'bg-cyan-500' : 'bg-slate-300'
                ]"
              >
                <div
                  :class="[
                    'absolute top-1 left-1 w-4 h-4 rounded-full bg-white transition-transform',
                    (settings as any)[item.key] ? 'translate-x-6' : ''
                  ]"
                />
              </button>
            </div>
          </div>
        </div>

        <!-- Security Section -->
        <div v-else-if="activeSection === 'security'" class="space-y-6">
          <div>
            <h2 :class="['text-xl font-medium mb-4', textPrimary]">安全与隐私</h2>
            <p :class="['text-sm mb-6', textSecondary]">保护您的账户安全</p>
          </div>

          <div class="space-y-4">
            <div :class="['p-4 rounded-xl border', cardBg]">
              <div class="flex items-center justify-between mb-4">
                <div>
                  <p :class="['text-sm font-medium mb-1', textPrimary]">双因素认证</p>
                  <p :class="['text-xs', textSecondary]">增强账户安全性</p>
                </div>
                <button
                  @click="settings.twoFactorAuth = !settings.twoFactorAuth"
                  :class="[
                    'relative w-12 h-6 rounded-full transition-colors',
                    settings.twoFactorAuth ? 'bg-cyan-500' : 'bg-slate-300'
                  ]"
                >
                  <div
                    :class="[
                      'absolute top-1 left-1 w-4 h-4 rounded-full bg-white transition-transform',
                      settings.twoFactorAuth ? 'translate-x-6' : ''
                    ]"
                  />
                </button>
              </div>
            </div>

            <div :class="['p-4 rounded-xl border', cardBg]">
              <label :class="['block text-sm font-medium mb-2', textPrimary]">会话超时时间（分钟）</label>
              <select
                v-model="settings.sessionTimeout"
                :class="['w-full px-4 py-2 border rounded-lg focus:outline-none focus:border-cyan-500/50', inputBg, textPrimary]"
              >
                <option value="15">15分钟</option>
                <option value="30">30分钟</option>
                <option value="60">60分钟</option>
                <option value="120">120分钟</option>
              </select>
            </div>

            <div :class="['p-4 rounded-xl border', cardBg]">
              <button class="w-full px-4 py-2 bg-yellow-500/20 text-yellow-600 border border-yellow-500/30 rounded-lg hover:bg-yellow-500/30 transition-all text-sm font-medium">
                修改密码
              </button>
            </div>
          </div>
        </div>

        <!-- Appearance Section -->
        <div v-else-if="activeSection === 'appearance'" class="space-y-6">
          <div>
            <h2 :class="['text-xl font-medium mb-4', textPrimary]">外观设置</h2>
            <p :class="['text-sm mb-6', textSecondary]">自定义界面外观和语言</p>
          </div>

          <div class="space-y-4">
            <div :class="['p-4 rounded-xl border', cardBg]">
              <label :class="['block text-sm font-medium mb-3', textSecondary]">主题模式</label>
              <div class="grid grid-cols-2 gap-3">
                <button
                  @click="theme = 'dark'"
                  :class="[
                    'p-4 rounded-lg border-2 transition-all',
                    theme === 'dark'
                      ? 'border-cyan-500 bg-cyan-500/10'
                      : 'border-slate-300 bg-slate-100 hover:border-slate-400'
                  ]"
                >
                  <div class="w-full h-20 rounded bg-gradient-to-br from-slate-800 to-slate-900 mb-2"></div>
                  <p :class="['text-sm text-center font-medium', textPrimary]">深色模式</p>
                </button>
                <button
                  @click="theme = 'light'"
                  :class="[
                    'p-4 rounded-lg border-2 transition-all',
                    theme === 'light'
                      ? 'border-cyan-500 bg-cyan-500/10'
                      : 'border-slate-600 bg-slate-700/50 hover:border-slate-500'
                  ]"
                >
                  <div class="w-full h-20 rounded bg-gradient-to-br from-gray-100 to-gray-200 mb-2"></div>
                  <p :class="['text-sm text-center font-medium', textPrimary]">浅色模式</p>
                </button>
              </div>
            </div>

            <div :class="['p-4 rounded-xl border', cardBg]">
              <label :class="['block text-sm font-medium mb-2', textSecondary]">语言</label>
              <select
                v-model="settings.language"
                :class="['w-full px-4 py-2 border rounded-lg focus:outline-none focus:border-cyan-500/50', inputBg, textPrimary]"
              >
                <option value="zh-CN">简体中文</option>
                <option value="en-US">English (US)</option>
                <option value="ja-JP">日本語</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Data Section -->
        <div v-else-if="activeSection === 'data'" class="space-y-6">
          <div>
            <h2 :class="['text-xl font-medium mb-4', textPrimary]">数据管理</h2>
            <p :class="['text-sm mb-6', textSecondary]">管理数据备份和存储设置</p>
          </div>

          <div class="space-y-4">
            <div :class="['p-4 rounded-xl border', cardBg]">
              <div class="flex items-center justify-between mb-4">
                <div>
                  <p :class="['text-sm font-medium mb-1', textPrimary]">自动备份</p>
                  <p :class="['text-xs', textSecondary]">定期自动备份您的数据</p>
                </div>
                <button
                  @click="settings.autoBackup = !settings.autoBackup"
                  :class="[
                    'relative w-12 h-6 rounded-full transition-colors',
                    settings.autoBackup ? 'bg-cyan-500' : 'bg-slate-300'
                  ]"
                >
                  <div
                    :class="[
                      'absolute top-1 left-1 w-4 h-4 rounded-full bg-white transition-transform',
                      settings.autoBackup ? 'translate-x-6' : ''
                    ]"
                  />
                </button>
              </div>
            </div>

            <div :class="['p-4 rounded-xl border', cardBg]">
              <label :class="['block text-sm font-medium mb-2', textSecondary]">备份频率</label>
              <select
                v-model="settings.backupFrequency"
                :disabled="!settings.autoBackup"
                :class="['w-full px-4 py-2 border rounded-lg focus:outline-none focus:border-cyan-500/50 disabled:opacity-50', inputBg, textPrimary]"
              >
                <option value="hourly">每小时</option>
                <option value="daily">每天</option>
                <option value="weekly">每周</option>
              </select>
            </div>

            <div :class="['p-4 rounded-xl border', cardBg]">
              <label :class="['block text-sm font-medium mb-2', textPrimary]">数据保留期限（天）</label>
              <input
                v-model="settings.dataRetention"
                type="number"
                :class="['w-full px-4 py-2 border rounded-lg focus:outline-none focus:border-cyan-500/50', inputBg, textPrimary]"
              />
              <p :class="['text-xs mt-2', textSecondary]">超过此期限的数据将被自动清理</p>
            </div>

            <div class="p-4 rounded-xl bg-red-500/10 border border-red-500/30">
              <p class="text-sm text-red-600 font-medium mb-3">危险操作</p>
              <button class="w-full px-4 py-2 bg-red-500/20 text-red-600 border border-red-500/30 rounded-lg hover:bg-red-500/30 transition-all text-sm font-medium">
                清除所有数据
              </button>
            </div>
          </div>
        </div>

        <!-- System Section -->
        <div v-else-if="activeSection === 'system'" class="space-y-6">
          <div>
            <h2 :class="['text-xl font-medium mb-4', textPrimary]">系统设置</h2>
            <p :class="['text-sm mb-6', textSecondary]">系统信息和高级设置</p>
          </div>

          <div class="space-y-4">
            <div :class="['p-4 rounded-xl border', cardBg]">
              <h3 :class="['text-sm font-medium mb-3', textPrimary]">系统信息</h3>
              <div class="space-y-2 text-sm">
                <div class="flex justify-between">
                  <span :class="textSecondary">系统版本</span>
                  <span :class="textPrimary">v3.2.1</span>
                </div>
                <div class="flex justify-between">
                  <span :class="textSecondary">最后更新</span>
                  <span :class="textPrimary">2026-01-03</span>
                </div>
                <div class="flex justify-between">
                  <span :class="textSecondary">数据库版本</span>
                  <span :class="textPrimary">PostgreSQL 15.2</span>
                </div>
                <div class="flex justify-between">
                  <span :class="textSecondary">API版本</span>
                  <span :class="textPrimary">v3.0.0</span>
                </div>
              </div>
            </div>

            <div :class="['p-4 rounded-xl border', cardBg]">
              <h3 :class="['text-sm font-medium mb-3', textPrimary]">存储使用情况</h3>
              <div class="mb-2">
                <div :class="['flex justify-between text-sm mb-1', textSecondary]">
                  <span>已使用</span>
                  <span :class="textPrimary">12.4 GB / 50 GB</span>
                </div>
                <div :class="['w-full h-2 rounded-full overflow-hidden', theme === 'dark' ? 'bg-slate-700' : 'bg-slate-200']">
                  <div class="h-full bg-gradient-to-r from-cyan-500 to-blue-600" style="width: 24.8%"></div>
                </div>
              </div>
            </div>

            <div :class="['p-4 rounded-xl border', cardBg]">
              <button class="w-full px-4 py-2 bg-cyan-500/20 text-cyan-600 border border-cyan-500/30 rounded-lg hover:bg-cyan-500/30 transition-all text-sm font-medium">
                检查更新
              </button>
            </div>
          </div>
        </div>

        <!-- Save Button -->
        <div :class="['flex gap-3 mt-8 pt-6 border-t', borderClass]">
          <button
            @click="handleSave"
            class="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 rounded-lg transition-all text-white font-medium"
          >
            <el-icon :size="18"><Check /></el-icon>
            <span>保存更改</span>
          </button>
          <button :class="[
            'px-6 py-3 rounded-lg transition-all font-medium',
            theme === 'dark' ? 'bg-slate-800 hover:bg-slate-700' : 'bg-slate-200 hover:bg-slate-300',
            textPrimary
          ]">
            取消
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 保持与 React 版本一致 */
</style>
