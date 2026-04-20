<template>
  <view class="page">
    <!-- 模式切换 -->
    <view class="mode-tabs">
      <view 
        :class="['mode-tab', { active: mode === 'batch' }]"
        @click="mode = 'batch'"
      >
        <text class="tab-icon">📋</text>
        <text>批量添加</text>
      </view>
      <view 
        :class="['mode-tab', { active: mode === 'single' }]"
        @click="mode = 'single'"
      >
        <text class="tab-icon">✏️</text>
        <text>单条添加</text>
      </view>
    </view>
    
    <view class="form-content">
      <!-- 批量添加模式 -->
      <view v-if="mode === 'batch'">
        <view class="form-card">
          <!-- 说明 -->
          <view class="tips-section">
            <view class="tips-item">• 每行一条，格式：日期 姓名</view>
            <view class="tips-item">• 公历：0408 妈妈 / 1204 张三@朋友</view>
            <view class="tips-item">• 农历：正月十五 爸爸 / 七月廿二 李四@同事</view>
            <view class="tips-item">• @后缀：@家人/@朋友/@同事/@客户</view>
          </view>
          
          <!-- 分组选择 -->
          <view class="form-section">
            <view class="section-icon">📁</view>
            <view class="section-body">
              <view class="form-label">默认分组</view>
              <picker mode="selector" :range="groupOptions" range-key="label" @change="changeBatchGroup">
                <view class="picker-value">
                  {{ getGroupLabel(batchGroup) }}
                  <text class="picker-arrow">›</text>
                </view>
              </picker>
            </view>
          </view>
          
          <!-- 文本输入 -->
          <view class="form-section text-section">
            <view class="form-label">导入内容</view>
            <textarea 
              class="text-input" 
              v-model="importText" 
              :placeholder="placeholderText"
              :maxlength="5000"
            ></textarea>
          </view>
          
          <!-- 预览 -->
          <view class="preview-section" v-if="parsedItems.length > 0">
            <view class="preview-title">预览 ({{ parsedItems.length }}条)</view>
            <view class="preview-list">
              <view class="preview-item" v-for="(item, index) in parsedItems" :key="index">
                <text class="preview-date">
                  <text v-if="item.lunar" class="lunar-tag">农历</text>
                  {{ item.displayDate }}
                </text>
                <text class="preview-name">{{ item.name }}</text>
                <text class="preview-group">{{ getGroupLabel(item.group_type) }}</text>
              </view>
            </view>
          </view>
          
          <button class="btn-import" @click="startImport" :disabled="loading || parsedItems.length === 0">
            <text class="btn-icon">✓</text>
            {{ loading ? '导入中...' : '开始导入' }}
          </button>
        </view>
      </view>
      
      <!-- 单条添加模式 -->
      <view v-if="mode === 'single'">
        <view class="form-card">
          <!-- 类型选择 -->
          <view class="form-section">
            <view class="section-icon">🎯</view>
            <view class="section-body">
              <view class="form-label">记录类型</view>
              <picker mode="selector" :range="typeOptions" range-key="label" @change="changeType">
                <view class="picker-value">
                  {{ typeOptions[singleForm.type - 1].label }}
                  <text class="picker-arrow">›</text>
                </view>
              </picker>
            </view>
          </view>
          
          <!-- 姓名 -->
          <view class="form-section">
            <view class="section-icon">👤</view>
            <view class="section-body">
              <view class="form-label">{{ singleForm.type === 1 ? '姓名' : '标题' }}</view>
              <input class="input" v-model="singleForm.name" :placeholder="singleForm.type === 1 ? '请输入姓名' : '请输入标题'" />
            </view>
          </view>
          
          <!-- 分组 -->
          <view class="form-section">
            <view class="section-icon">📁</view>
            <view class="section-body">
              <view class="form-label">分组</view>
              <picker mode="selector" :range="groupOptions" range-key="label" @change="changeSingleGroup">
                <view class="picker-value">
                  {{ getGroupLabel(singleForm.group_type) }}
                  <text class="picker-arrow">›</text>
                </view>
              </picker>
            </view>
          </view>
        </view>
        
        <view class="form-card">
          <view class="card-title">
            <text class="title-icon">📅</text>
            <text>日期信息</text>
          </view>
          
          <!-- 日期类型 -->
          <view class="form-section">
            <view class="section-icon">🗓️</view>
            <view class="section-body">
              <view class="form-label">日期类型</view>
              <picker mode="selector" :range="dateTypeOptions" range-key="label" @change="changeDateType">
                <view class="picker-value">
                  {{ dateTypeOptions[singleForm.date_type - 1].label }}
                  <text class="picker-arrow">›</text>
                </view>
              </picker>
            </view>
          </view>
          
          <!-- 日期选择 -->
          <view class="form-row">
            <view class="form-section half">
              <view class="section-icon">📆</view>
              <view class="section-body">
                <view class="form-label">月份</view>
                <picker mode="selector" :range="monthRange" @change="e => singleForm.month = parseInt(e.detail.value) + 1">
                  <view class="picker-value">
                    {{ singleForm.month || '选择' }}
                    <text class="picker-arrow">›</text>
                  </view>
                </picker>
              </view>
            </view>
            <view class="form-section half">
              <view class="section-icon">🌞</view>
              <view class="section-body">
                <view class="form-label">日期</view>
                <picker mode="selector" :range="dayRange" @change="e => singleForm.day = parseInt(e.detail.value) + 1">
                  <view class="picker-value">
                    {{ singleForm.day || '选择' }}
                    <text class="picker-arrow">›</text>
                  </view>
                </picker>
              </view>
            </view>
          </view>
          
          <!-- 出生年份（仅生日） -->
          <view class="form-section" v-if="singleForm.type === 1">
            <view class="section-icon">🎂</view>
            <view class="section-body">
              <view class="form-label">出生年份 <text class="label-hint">（选填）</text></view>
              <input class="input" v-model="singleForm.year" type="number" placeholder="例如：1990" />
            </view>
          </view>
        </view>
        
        <button class="btn-save" @click="saveSingle" :disabled="loading">
          <text class="btn-icon">✓</text>
          {{ loading ? '保存中...' : '保存' }}
        </button>
      </view>
    </view>
  </view>
</template>

<script>
import { recordApi } from '../../api/index.js';

export default {
  data() {
    return {
      mode: 'batch', // 默认批量添加
      loading: false,
      
      // 批量导入
      importText: '',
      batchGroup: 1,
      placeholderText: '例如：\n0408 妈妈\n正月十五 爸爸\n1204 张三@朋友\n七月廿二 李四@同事',
      groupOptions: [
        { label: '家人', value: 1 },
        { label: '朋友', value: 2 },
        { label: '同事', value: 3 },
        { label: '客户', value: 4 }
      ],
      
      // 单条添加
      singleForm: {
        type: 1,
        name: '',
        group_type: 1,
        date_type: 1,
        month: null,
        day: null,
        year: ''
      },
      typeOptions: [
        { label: '生日', value: 1 },
        { label: '纪念日', value: 2 }
      ],
      dateTypeOptions: [
        { label: '公历', value: 1 },
        { label: '农历', value: 2 }
      ],
      monthRange: Array.from({ length: 12 }, (_, i) => (i + 1) + '月'),
      dayRange: Array.from({ length: 31 }, (_, i) => (i + 1) + '日')
    };
  },
  
  computed: {
    parsedItems() {
      const items = [];
      const lines = this.importText.split('\n').filter(l => l.trim());
      const groupMap = {
        '家人': 1, '朋友': 2, '同事': 3, '客户': 4
      };
      
      for (const line of lines) {
        const parts = line.trim().split(/\s+/);
        if (parts.length < 2) continue;
        
        let dateStr = parts[0];
        let name = parts.slice(1).join(' ');
        let groupType = this.batchGroup;
        let isLunar = false;
        
        // 检查姓名后是否带分组
        if (name.includes('@')) {
          const [realName, groupStr] = name.split('@');
          name = realName;
          groupType = groupMap[groupStr] || this.batchGroup;
        }
        
        // 解析日期
        if (dateStr.includes('月') || dateStr.includes('初') || dateStr.includes('廿')) {
          isLunar = true;
          const lunarMap = {
            '正': 1, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
            '六': 6, '七': 7, '八': 8, '九': 9, '十': 10, '冬': 11, '腊': 12
          };
          const dayMap = {
            '初一': 1, '初二': 2, '初三': 3, '初四': 4, '初五': 5,
            '初六': 6, '初七': 7, '初八': 8, '初九': 9, '初十': 10,
            '十一': 11, '十二': 12, '十三': 13, '十四': 14, '十五': 15,
            '十六': 16, '十七': 17, '十八': 18, '十九': 19, '二十': 20,
            '廿一': 21, '廿二': 22, '廿三': 23, '廿四': 24, '廿五': 25,
            '廿六': 26, '廿七': 27, '廿八': 28, '廿九': 29, '三十': 30
          };
          
          let month = 1, day = 1;
          for (const [k, v] of Object.entries(lunarMap)) {
            if (dateStr.startsWith(k) || dateStr.startsWith(k + '月')) {
              month = v;
              break;
            }
          }
          for (const [k, v] of Object.entries(dayMap)) {
            if (dateStr.includes(k)) {
              day = v;
              break;
            }
          }
          
          items.push({
            date: dateStr,
            name: name,
            group_type: groupType,
            lunar: true,
            displayDate: `${month}/${day}`
          });
        } else if (/^\d{4}$/.test(dateStr)) {
          const month = parseInt(dateStr.slice(0, 2));
          const day = parseInt(dateStr.slice(2));
          items.push({
            date: dateStr,
            name: name,
            group_type: groupType,
            lunar: false,
            displayDate: `${month}/${day}`
          });
        }
      }
      
      return items;
    }
  },
  
  methods: {
    goBack() {
      uni.navigateBack();
    },
    
    getGroupLabel(type) {
      const names = { 1: '家人', 2: '朋友', 3: '同事', 4: '客户' };
      return names[type] || '其他';
    },
    
    // 批量导入方法
    changeBatchGroup(e) {
      this.batchGroup = this.groupOptions[e.detail.value].value;
    },
    
    async startImport() {
      if (this.parsedItems.length === 0) {
        return uni.showToast({ title: '请输入导入内容', icon: 'none' });
      }
      
      this.loading = true;
      try {
        const items = this.parsedItems.map(item => ({
          date: item.date,
          name: item.name,
          type: 1,
          lunar: item.lunar
        }));
        
        const result = await recordApi.batchImport(items, this.batchGroup);
        
        uni.showModal({
          title: '导入完成',
          content: `成功导入 ${result.imported} 条${result.failed > 0 ? `，失败 ${result.failed} 条` : ''}`,
          showCancel: false,
          success: () => {
            uni.navigateBack();
          }
        });
      } catch (e) {
        uni.showToast({ title: e.detail || '导入失败', icon: 'none' });
      } finally {
        this.loading = false;
      }
    },
    
    // 单条添加方法
    changeType(e) {
      this.singleForm.type = parseInt(e.detail.value) + 1;
    },
    
    changeSingleGroup(e) {
      this.singleForm.group_type = this.groupOptions[e.detail.value].value;
    },
    
    changeDateType(e) {
      this.singleForm.date_type = parseInt(e.detail.value) + 1;
    },
    
    async saveSingle() {
      if (!this.singleForm.name.trim()) {
        return uni.showToast({ title: '请输入姓名', icon: 'none' });
      }
      if (!this.singleForm.month || !this.singleForm.day) {
        return uni.showToast({ title: '请选择日期', icon: 'none' });
      }
      
      this.loading = true;
      try {
        const yearVal = this.singleForm.year && this.singleForm.year !== '' ? parseInt(this.singleForm.year) : null;
        
        await recordApi.create({
          type: this.singleForm.type,
          name: this.singleForm.name,
          group_type: this.singleForm.group_type,
          date_type: this.singleForm.date_type,
          month: parseInt(this.singleForm.month),
          day: parseInt(this.singleForm.day),
          year: yearVal,
          remind_type: '1,7',
          sms_remind: 0
        });
        
        uni.showToast({ title: '添加成功', icon: 'success' });
        setTimeout(() => uni.navigateBack(), 1500);
      } catch (e) {
        uni.showToast({ title: e.detail || '保存失败', icon: 'none' });
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: linear-gradient(180deg, #FFF8F9 0%, #FFF0F5 100%);
}

/* 顶部导航 */
.header-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(135deg, #FF9A8B 0%, #FF6A88 100%);
  padding: 60rpx 32rpx 32rpx;
  color: white;
}

.back-btn {
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
}

.back-icon {
  font-size: 48rpx;
  font-weight: bold;
  line-height: 1;
}

.header-title {
  font-size: 34rpx;
  font-weight: 600;
}

.header-placeholder {
  width: 64rpx;
}

/* 模式切换 */
.mode-tabs {
  display: flex;
  gap: 14rpx;
  padding: 20rpx 24rpx;
  background: white;
  border-bottom: 1rpx solid #FFE4E8;
}

.mode-tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  padding: 16rpx;
  border-radius: 18rpx;
  background: #FFF5F7;
  color: #A0522D;
  font-size: 26rpx;
  transition: all 0.3s ease;
}

.mode-tab.active {
  background: linear-gradient(135deg, #FFB6C1, #FFC0CB);
  color: #8B4513;
  box-shadow: 0 4rpx 12rpx rgba(255, 183, 193, 0.4);
}

.tab-icon {
  font-size: 28rpx;
}

/* 表单内容 */
.form-content {
  padding: 28rpx;
}

/* 表单卡片 */
.form-card {
  background: white;
  border-radius: 24rpx;
  padding: 28rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.05);
}

.card-title {
  display: flex;
  align-items: center;
  gap: 12rpx;
  font-size: 30rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 28rpx;
  padding-bottom: 20rpx;
  border-bottom: 2rpx solid #FFF5F3;
}

.title-icon {
  font-size: 32rpx;
}

/* 提示信息 */
.tips-section {
  background: #FFF9F7;
  border-radius: 16rpx;
  padding: 20rpx 24rpx;
  margin-bottom: 24rpx;
}

.tips-item {
  font-size: 24rpx;
  color: #666;
  line-height: 1.8;
}

/* 表单项 */
.form-section {
  display: flex;
  align-items: flex-start;
  padding: 20rpx 0;
  border-bottom: 1rpx solid #F8F8F8;
}

.form-section:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.section-icon {
  font-size: 32rpx;
  margin-right: 16rpx;
  margin-top: 2rpx;
}

.section-body {
  flex: 1;
}

.form-label {
  font-size: 24rpx;
  color: #999;
  margin-bottom: 8rpx;
}

.label-hint {
  font-size: 22rpx;
  color: #CCC;
}

.picker-value {
  font-size: 30rpx;
  color: #333;
  font-weight: 500;
  display: flex;
  align-items: center;
}

.picker-arrow {
  margin-left: auto;
  font-size: 32rpx;
  color: #CCC;
}

.input {
  font-size: 30rpx;
  color: #333;
  padding: 4rpx 0;
}

/* 日期行 */
.form-row {
  display: flex;
  gap: 20rpx;
}

.form-section.half {
  flex: 1;
}

/* 文本输入 */
.text-section {
  padding: 20rpx 0;
}

.text-input {
  width: 100%;
  min-height: 200rpx;
  font-size: 28rpx;
  line-height: 1.8;
  color: #333;
}

/* 预览 */
.preview-section {
  background: #FFF9F7;
  border-radius: 16rpx;
  padding: 20rpx;
  margin-bottom: 24rpx;
}

.preview-title {
  font-size: 24rpx;
  color: #999;
  margin-bottom: 16rpx;
}

.preview-item {
  display: flex;
  align-items: center;
  padding: 12rpx 0;
  border-bottom: 1rpx solid #FFE8E3;
}

.preview-item:last-child {
  border-bottom: none;
}

.preview-date {
  width: 140rpx;
  font-size: 24rpx;
  color: #FF6A88;
  display: flex;
  align-items: center;
  gap: 6rpx;
}

.lunar-tag {
  background: #FFB7C5;
  color: white;
  padding: 2rpx 8rpx;
  border-radius: 6rpx;
  font-size: 18rpx;
}

.preview-name {
  flex: 1;
  font-size: 26rpx;
  color: #333;
}

.preview-group {
  font-size: 22rpx;
  color: #999;
}

/* 按钮 */
.btn-import, .btn-save {
  width: 100%;
  background: linear-gradient(135deg, #FFB6C1, #FFC0CB);
  color: #8B4513;
  border-radius: 36rpx;
  padding: 20rpx;
  font-size: 28rpx;
  font-weight: 500;
  margin-top: 24rpx;
  border: none;
  box-shadow: 0 4rpx 12rpx rgba(255, 183, 193, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6rpx;
}

.btn-import:active, .btn-save:active {
  opacity: 0.9;
}

.btn-icon {
  font-size: 26rpx;
}
</style>
