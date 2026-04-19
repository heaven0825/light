<template>
  <view class="page">
    <view class="nav-bar">
      <text class="nav-title">发送短信</text>
    </view>
    
    <view class="content">
      <!-- 收信人信息 -->
      <view class="recipient-section card">
        <view class="recipient-name">{{ recordName }}</view>
        <input 
          class="phone-input" 
          v-model="mobile" 
          type="number" 
          placeholder="请输入手机号" 
          maxlength="11"
        />
      </view>
      
      <!-- 祝福语选择 -->
      <view class="blessing-section card">
        <view class="section-title">选择祝福语</view>
        <view class="blessing-list">
          <view 
            v-for="item in blessings" 
            :key="item.id"
            :class="['blessing-item', { active: selectedBlessing === item.content }]"
            @click="selectBlessing(item.content)"
          >
            {{ item.content }}
          </view>
        </view>
      </view>
      
      <!-- 短信预览 -->
      <view class="preview-section card">
        <view class="section-title">短信预览</view>
        <view class="preview-content">{{ smsContent || '请选择或编辑祝福语' }}</view>
      </view>
      
      <!-- 发送按钮 -->
      <button class="btn-send" @click="sendSms" :disabled="loading || !mobile">
        {{ loading ? '发送中...' : '发送短信' }}
      </button>
      
      <!-- 短信余额 -->
      <view class="sms-remaining" v-if="remaining !== null">
        剩余短信：{{ remaining === '无限' ? '无限' : remaining + '条' }}
      </view>
    </view>
  </view>
</template>

<script>
import { smsApi, blessingApi, recordApi } from '../../api/index.js';

export default {
  data() {
    return {
      recordId: null,
      recordName: '',
      mobile: '',
      blessings: [],
      selectedBlessing: '',
      smsContent: '',
      remaining: null,
      loading: false
    };
  },
  
  onLoad(options) {
    this.recordId = options.id;
    this.recordName = decodeURIComponent(options.name || '');
    this.loadData();
  },
  
  methods: {
    async loadData() {
      try {
        // 获取祝福语
        const blessings = await blessingApi.getList(1); // 默认家人分组
        this.blessings = blessings;
        
        // 获取剩余短信
        const remaining = await smsApi.getRemaining();
        this.remaining = remaining.unlimited ? '无限' : remaining.count;
      } catch (e) {
        console.error(e);
      }
    },
    
    selectBlessing(content) {
      this.selectedBlessing = content;
      this.smsContent = `【时光记】亲爱的朋友，${content} 祝一切顺利！`;
    },
    
    async sendSms() {
      if (!this.mobile || this.mobile.length !== 11) {
        return uni.showToast({ title: '请输入正确的手机号', icon: 'none' });
      }
      
      if (!this.smsContent) {
        return uni.showToast({ title: '请选择祝福语', icon: 'none' });
      }
      
      this.loading = true;
      try {
        const result = await smsApi.send({
          record_id: this.recordId,
          mobile: this.mobile,
          content: this.smsContent
        });
        
        uni.showToast({ title: '发送成功', icon: 'success' });
        this.remaining = result.remaining;
        
        setTimeout(() => uni.navigateBack(), 1500);
      } catch (e) {
        uni.showToast({ title: e.detail || '发送失败', icon: 'none' });
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

.content {
  padding: 24rpx;
}

.card {
  background: white;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 24rpx;
}

.recipient-name {
  font-size: 32rpx;
  font-weight: 600;
  margin-bottom: 20rpx;
}

.phone-input {
  font-size: 30rpx;
  padding: 20rpx;
  border: 2rpx solid #EEE;
  border-radius: 12rpx;
}

.section-title {
  font-size: 28rpx;
  font-weight: 600;
  margin-bottom: 20rpx;
}

.blessing-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.blessing-item {
  padding: 20rpx;
  background: #F8F9FA;
  border-radius: 12rpx;
  font-size: 26rpx;
  line-height: 1.6;
  border: 2rpx solid transparent;
}

.blessing-item.active {
  background: #E6F7FF;
  border-color: #4A90E2;
}

.preview-content {
  padding: 24rpx;
  background: #F8F9FA;
  border-radius: 12rpx;
  font-size: 26rpx;
  line-height: 1.6;
  color: #333;
}

.btn-send {
  width: 100%;
  background: linear-gradient(135deg, #4A90E2, #667EE5);
  color: white;
  border-radius: 44rpx;
  padding: 28rpx;
  font-size: 32rpx;
  border: none;
}

.sms-remaining {
  text-align: center;
  color: #999;
  font-size: 24rpx;
  margin-top: 20rpx;
}
</style>
