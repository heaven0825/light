<template>
  <view class="page">
    <view class="form-content">
      <!-- 类型选择 -->
      <view class="form-card">
        <view class="form-section">
          <view class="section-icon">🎯</view>
          <view class="section-body">
            <view class="form-label">记录类型</view>
            <picker mode="selector" :range="typeOptions" range-key="label" @change="changeType">
              <view class="picker-value">
                {{ typeOptions[form.type - 1].label }}
                <text class="picker-arrow">›</text>
              </view>
            </picker>
          </view>
        </view>
      </view>
      
      <!-- 基本信息 -->
      <view class="form-card">
        <view class="form-section">
          <view class="section-icon">👤</view>
          <view class="section-body">
            <view class="form-label">{{ form.type === 1 ? '姓名' : '标题' }}</view>
            <input class="input" v-model="form.name" :placeholder="form.type === 1 ? '请输入姓名' : '请输入标题'" />
          </view>
        </view>
        
        <view class="form-section">
          <view class="section-icon">📁</view>
          <view class="section-body">
            <view class="form-label">分组</view>
            <picker mode="selector" :range="groupOptions" range-key="label" @change="changeGroup">
              <view class="picker-value">
                {{ getGroupLabel(form.group_type) }}
                <text class="picker-arrow">›</text>
              </view>
            </picker>
          </view>
        </view>
      </view>
      
      <!-- 日期信息 -->
      <view class="form-card">
        <view class="form-section">
          <view class="section-icon">🗓️</view>
          <view class="section-body">
            <view class="form-label">日期类型</view>
            <picker mode="selector" :range="dateTypeOptions" range-key="label" @change="changeDateType">
              <view class="picker-value">
                {{ dateTypeOptions[form.date_type - 1].label }}
                <text class="picker-arrow">›</text>
              </view>
            </picker>
          </view>
        </view>
        
        <view class="form-row">
          <view class="form-section half">
            <view class="section-icon">📆</view>
            <view class="section-body">
              <view class="form-label">月份</view>
              <picker mode="selector" :range="monthRange" @change="e => form.month = parseInt(e.detail.value) + 1">
                <view class="picker-value">
                  {{ form.month || '选择' }}
                  <text class="picker-arrow">›</text>
                </view>
              </picker>
            </view>
          </view>
          <view class="form-section half">
            <view class="section-icon">🌞</view>
            <view class="section-body">
              <view class="form-label">日期</view>
              <picker mode="selector" :range="dayRange" @change="e => form.day = parseInt(e.detail.value) + 1">
                <view class="picker-value">
                  {{ form.day || '选择' }}
                  <text class="picker-arrow">›</text>
                </view>
              </picker>
            </view>
          </view>
        </view>
        
        <view class="form-section" v-if="form.type === 1">
          <view class="section-icon">🎂</view>
          <view class="section-body">
            <view class="form-label">出生年份 <text class="label-hint">（选填，用于计算年龄）</text></view>
            <input class="input" v-model="form.year" type="number" placeholder="例如：1990" />
          </view>
        </view>
      </view>
      
      <!-- 提醒设置 -->
      <view class="form-card">
        <view class="form-section remind-section">
          <view class="remind-tags">
            <view 
              v-for="opt in remindOptions" 
              :key="opt.value"
              :class="['remind-tag', { active: selectedReminds.includes(opt.value) }]"
              @click="toggleRemind(opt.value)"
            >
              <text class="tag-icon">{{ opt.icon }}</text>
              <text>{{ opt.label }}</text>
            </view>
          </view>
        </view>
        
        <view class="form-section switch-section">
          <view class="section-icon">💬</view>
          <view class="section-body">
            <view class="form-label">短信提醒</view>
            <view class="switch-desc">提前一天发送短信提醒</view>
          </view>
          <switch :checked="form.sms_remind === 1" @change="toggleSms" color="#FF6A88" />
        </view>
      </view>
      
      <!-- 保存按钮 -->
      <button class="btn-save" @click="save" :disabled="loading">
        <text class="btn-icon">✓</text>
        {{ loading ? '保存中...' : '保存' }}
      </button>
      
      <!-- 删除按钮 -->
      <button class="btn-delete" @click="deleteRecord" v-if="form.id">
        <text class="btn-icon">✕</text>
        删除记录
      </button>
    </view>
  </view>
</template>

<script>
import { recordApi } from '../../api/index.js';

export default {
  data() {
    return {
      form: {
        id: null,
        type: 1,
        name: '',
        group_type: 1,
        date_type: 1,
        month: '',
        day: '',
        year: '',
        remind_type: '1,7',
        sms_remind: 0
      },
      typeOptions: [
        { label: '生日', value: 1 },
        { label: '纪念日', value: 2 }
      ],
      groupOptions: [
        { label: '家人', value: 1 },
        { label: '朋友', value: 2 },
        { label: '同事', value: 3 },
        { label: '客户', value: 4 }
      ],
      dateTypeOptions: [
        { label: '公历', value: 1 },
        { label: '农历', value: 2 }
      ],
      remindOptions: [
        { label: '1天', value: '1', icon: '📱' },
        { label: '3天', value: '3', icon: '📅' },
        { label: '7天', value: '7', icon: '📆' },
        { label: '14天', value: '14', icon: '🗓️' }
      ],
      selectedReminds: ['1', '7'],
      loading: false,
      monthRange: Array.from({ length: 12 }, (_, i) => (i + 1) + '月'),
      dayRange: Array.from({ length: 31 }, (_, i) => (i + 1) + '日')
    };
  },
  
  onLoad(options) {
    if (options.id) {
      this.form.id = parseInt(options.id);
      this.loadRecord();
    }
  },
  
  methods: {
    goBack() {
      uni.navigateBack();
    },
    
    async loadRecord() {
      try {
        const record = await recordApi.getOne(this.form.id);
        this.form = {
          id: record.id,
          type: record.type,
          name: record.name,
          group_type: record.group_type,
          date_type: record.date_type,
          month: record.month,
          day: record.day,
          year: record.year || '',
          remind_type: record.remind_type || '1,7',
          sms_remind: record.sms_remind || 0
        };
        if (record.remind_type) {
          this.selectedReminds = record.remind_type.split(',');
        }
      } catch (e) {
        uni.showToast({ title: '加载失败', icon: 'none' });
      }
    },
    
    changeType(e) {
      this.form.type = parseInt(e.detail.value) + 1;
    },
    
    changeGroup(e) {
      this.form.group_type = parseInt(e.detail.value) + 1;
    },
    
    changeDateType(e) {
      this.form.date_type = parseInt(e.detail.value) + 1;
    },
    
    getGroupLabel(type) {
      const names = { 1: '家人', 2: '朋友', 3: '同事', 4: '客户' };
      return names[type] || '其他';
    },
    
    toggleRemind(value) {
      const index = this.selectedReminds.indexOf(value);
      if (index > -1) {
        this.selectedReminds.splice(index, 1);
      } else {
        this.selectedReminds.push(value);
      }
      this.form.remind_type = this.selectedReminds.join(',');
    },
    
    toggleSms() {
      this.form.sms_remind = this.form.sms_remind ? 0 : 1;
    },
    
    async save() {
      if (!this.form.name.trim()) {
        return uni.showToast({ title: '请输入姓名', icon: 'none' });
      }
      if (!this.form.month || !this.form.day) {
        return uni.showToast({ title: '请选择日期', icon: 'none' });
      }
      
      this.loading = true;
      try {
        // 构建提交数据
        const yearVal = this.form.year && this.form.year !== '' ? parseInt(this.form.year) : null;
        
        if (this.form.id) {
          await recordApi.update(this.form.id, {
            type: this.form.type,
            name: this.form.name,
            group_type: this.form.group_type,
            date_type: this.form.date_type,
            month: parseInt(this.form.month),
            day: parseInt(this.form.day),
            year: yearVal,
            remind_type: this.form.remind_type,
            sms_remind: this.form.sms_remind
          });
          uni.showToast({ title: '更新成功', icon: 'success' });
        } else {
          await recordApi.create({
            type: this.form.type,
            name: this.form.name,
            group_type: this.form.group_type,
            date_type: this.form.date_type,
            month: parseInt(this.form.month),
            day: parseInt(this.form.day),
            year: yearVal,
            remind_type: this.form.remind_type,
            sms_remind: this.form.sms_remind
          });
          uni.showToast({ title: '添加成功', icon: 'success' });
        }
        setTimeout(() => uni.navigateBack(), 1500);
      } catch (e) {
        uni.showToast({ title: e.detail || '保存失败', icon: 'none' });
      } finally {
        this.loading = false;
      }
    },
    
    async deleteRecord() {
      if (!this.form.id) return;
      
      uni.showModal({
        title: '确认删除',
        content: '确定要删除这条记录吗？',
        success: async (res) => {
          if (res.confirm) {
            try {
              await recordApi.delete(this.form.id);
              uni.showToast({ title: '已删除', icon: 'success' });
              setTimeout(() => uni.navigateBack(), 1500);
            } catch (e) {
              uni.showToast({ title: '删除失败', icon: 'none' });
            }
          }
        }
      });
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

.form-section {
  display: flex;
  align-items: flex-start;
  padding: 24rpx 0;
  border-bottom: 1rpx solid #F8F8F8;
}

.form-section:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.section-icon {
  font-size: 36rpx;
  margin-right: 20rpx;
  margin-top: 4rpx;
}

.section-body {
  flex: 1;
}

.form-label {
  font-size: 24rpx;
  color: #999;
  margin-bottom: 10rpx;
}

.label-hint {
  font-size: 22rpx;
  color: #CCC;
}

.picker-value {
  font-size: 32rpx;
  color: #333;
  font-weight: 500;
  display: flex;
  align-items: center;
}

.picker-arrow {
  margin-left: auto;
  font-size: 36rpx;
  color: #CCC;
}

.input {
  font-size: 32rpx;
  color: #333;
  padding: 8rpx 0;
}

/* 日期选择行 */
.form-row {
  display: flex;
  gap: 20rpx;
}

.form-section.half {
  flex: 1;
}

/* 提醒设置 */
.remind-section {
  padding: 8rpx 0 24rpx;
}

.remind-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}

.remind-tag {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 14rpx 20rpx;
  border-radius: 25rpx;
  background: #FFF5F7;
  font-size: 24rpx;
  color: #A0522D;
  transition: all 0.3s ease;
}

.remind-tag.active {
  background: linear-gradient(135deg, #FFB6C1, #FFC0CB);
  color: #8B4513;
  box-shadow: 0 4rpx 12rpx rgba(255, 183, 193, 0.4);
}

.tag-icon {
  font-size: 24rpx;
}

/* 开关 */
.switch-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.switch-desc {
  font-size: 22rpx;
  color: #CCC;
  margin-top: 4rpx;
}

/* 按钮 */
.btn-save {
  width: 100%;
  background: linear-gradient(135deg, #FFB6C1, #FFC0CB);
  color: #8B4513;
  border-radius: 36rpx;
  padding: 20rpx;
  font-size: 28rpx;
  font-weight: 500;
  margin-top: 28rpx;
  border: none;
  box-shadow: 0 4rpx 12rpx rgba(255, 183, 193, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6rpx;
}

.btn-save:active {
  opacity: 0.9;
}

.btn-icon {
  font-size: 26rpx;
}

.btn-delete {
  width: 100%;
  background: white;
  color: #E899B8;
  border-radius: 36rpx;
  padding: 20rpx;
  font-size: 28rpx;
  font-weight: 500;
  margin-top: 16rpx;
  border: 1rpx solid #FFE4E8;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6rpx;
}

.btn-delete:active {
  background: #FFF5F5;
}
</style>
