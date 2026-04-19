<template>
  <view class="page">
    <!-- 顶部 -->
    <view class="nav-bar">
      <text class="nav-title">{{ form.id ? '编辑记录' : '添加记录' }}</text>
    </view>
    
    <view class="form-content">
      <!-- 类型选择 -->
      <view class="form-section">
        <view class="form-label">记录类型</view>
        <picker mode="selector" :range="typeOptions" range-key="label" @change="changeType">
          <view class="picker-value">{{ typeOptions[form.type - 1].label }}</view>
        </picker>
      </view>
      
      <!-- 姓名 -->
      <view class="form-section">
        <view class="form-label">{{ form.type === 1 ? '姓名' : '标题' }}</view>
        <input class="input" v-model="form.name" :placeholder="form.type === 1 ? '请输入姓名' : '请输入标题'" />
      </view>
      
      <!-- 分组 -->
      <view class="form-section">
        <view class="form-label">分组</view>
        <picker mode="selector" :range="groupOptions" range-key="label" @change="changeGroup">
          <view class="picker-value">{{ getGroupLabel(form.group_type) }}</view>
        </picker>
      </view>
      
      <!-- 日期类型 -->
      <view class="form-section">
        <view class="form-label">日期类型</view>
        <picker mode="selector" :range="dateTypeOptions" range-key="label" @change="changeDateType">
          <view class="picker-value">{{ dateTypeOptions[form.date_type - 1].label }}</view>
        </picker>
      </view>
      
      <!-- 日期选择 -->
      <view class="form-row">
        <view class="form-section half">
          <view class="form-label">月份</view>
          <picker mode="selector" :range="monthRange" @change="e => form.month = parseInt(e.detail.value) + 1">
            <view class="picker-value">{{ form.month || '请选择' }}</view>
          </picker>
        </view>
        <view class="form-section half">
          <view class="form-label">日期</view>
          <picker mode="selector" :range="dayRange" @change="e => form.day = parseInt(e.detail.value) + 1">
            <view class="picker-value">{{ form.day || '请选择' }}</view>
          </picker>
        </view>
      </view>
      
      <!-- 出生年份（仅生日） -->
      <view class="form-section" v-if="form.type === 1">
        <view class="form-label">出生年份（选填）</view>
        <input class="input" v-model="form.year" type="number" placeholder="用于计算年龄" />
      </view>
      
      <!-- 提醒设置 -->
      <view class="form-section">
        <view class="form-label">提醒设置</view>
        <view class="remind-tags">
          <view 
            v-for="opt in remindOptions" 
            :key="opt.value"
            :class="['remind-tag', { active: selectedReminds.includes(opt.value) }]"
            @click="toggleRemind(opt.value)"
          >{{ opt.label }}</view>
        </view>
      </view>
      
      <!-- 短信提醒 -->
      <view class="form-section switch-section">
        <view class="form-label">短信提醒</view>
        <switch :checked="form.sms_remind === 1" @change="toggleSms" color="#4A90E2" />
      </view>
      
      <!-- 保存按钮 -->
      <button class="btn-save" @click="save" :disabled="loading">
        {{ loading ? '保存中...' : '保存' }}
      </button>
      
      <!-- 删除按钮 -->
      <button class="btn-delete" @click="deleteRecord" v-if="form.id">
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
        { label: '提前1天', value: '1' },
        { label: '提前3天', value: '3' },
        { label: '提前7天', value: '7' },
        { label: '提前14天', value: '14' }
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
        if (this.form.id) {
          await recordApi.update(this.form.id, this.form);
          uni.showToast({ title: '更新成功', icon: 'success' });
        } else {
          await recordApi.create(this.form);
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
  background: #F5F7FA;
}

.nav-bar {
  background: white;
  padding: 60rpx 30rpx 30rpx;
  text-align: center;
}

.nav-title {
  font-size: 34rpx;
  font-weight: 600;
}

.form-content {
  padding: 24rpx;
}

.form-section {
  background: white;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
}

.form-row {
  display: flex;
  gap: 20rpx;
}

.form-section.half {
  flex: 1;
}

.form-label {
  font-size: 26rpx;
  color: #999;
  margin-bottom: 16rpx;
}

.picker-value {
  font-size: 30rpx;
  color: #333;
}

.input {
  font-size: 30rpx;
}

.remind-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}

.remind-tag {
  padding: 12rpx 24rpx;
  border-radius: 30rpx;
  background: #F0F0F0;
  font-size: 26rpx;
  color: #666;
}

.remind-tag.active {
  background: #4A90E2;
  color: white;
}

.switch-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.btn-save {
  width: 100%;
  background: linear-gradient(135deg, #4A90E2, #667EE5);
  color: white;
  border-radius: 44rpx;
  padding: 28rpx;
  font-size: 32rpx;
  margin-top: 40rpx;
  border: none;
}

.btn-delete {
  width: 100%;
  background: white;
  color: #FF6B6B;
  border-radius: 44rpx;
  padding: 28rpx;
  font-size: 32rpx;
  margin-top: 20rpx;
  border: 2rpx solid #FF6B6B;
}
</style>
