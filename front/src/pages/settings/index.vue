<template>
  <view class="page">
    <view class="nav-bar">
      <text class="nav-title">设置</text>
    </view>
    
    <view class="content">
      <!-- 用户信息 -->
      <view class="user-section card">
        <view class="user-info" v-if="userInfo">
          <image class="avatar" :src="userInfo.avatar || '/static/default-avatar.png'" mode="aspectFill" />
          <view class="user-detail">
            <text class="nickname">{{ userInfo.nickname || '微信用户' }}</text>
            <text class="user-type">{{ getVipName(userInfo.vip_type) }}</text>
          </view>
        </view>
      </view>
      
      <!-- 统计信息 -->
      <view class="stats-section card">
        <view class="stats-title">使用统计</view>
        <view class="stats-grid">
          <view class="stat-item">
            <text class="stat-num">{{ stats.record_count || 0 }}</text>
            <text class="stat-label">记录数</text>
          </view>
          <view class="stat-item">
            <text class="stat-num">{{ stats.record_limit || 8 }}</text>
            <text class="stat-label">上限</text>
          </view>
          <view class="stat-item">
            <text class="stat-num">{{ stats.sms_count || 3 }}</text>
            <text class="stat-label">短信条数</text>
          </view>
        </view>
      </view>
      
      <!-- 功能菜单 -->
      <view class="menu-section card">
        <view class="menu-item" @click="goToSmsLogs">
          <text class="menu-icon">📱</text>
          <text class="menu-text">短信记录</text>
          <text class="menu-arrow">></text>
        </view>
        <view class="menu-item" @click="clearCache">
          <text class="menu-icon">🗑️</text>
          <text class="menu-text">清理缓存</text>
          <text class="menu-arrow">></text>
        </view>
        <view class="menu-item" @click="showAbout">
          <text class="menu-icon">ℹ️</text>
          <text class="menu-text">关于我们</text>
          <text class="menu-arrow">></text>
        </view>
      </view>
      
      <!-- 版本信息 -->
      <view class="version-info">
        <text>时光记 v1.0.0</text>
      </view>
    </view>
  </view>
</template>

<script>
import { userApi } from '../../api/index.js';

export default {
  data() {
    return {
      userInfo: null,
      stats: {}
    };
  },
  
  onLoad() {
    this.loadData();
  },
  
  onShow() {
    this.loadData();
  },
  
  methods: {
    async loadData() {
      try {
        const [userInfo, stats] = await Promise.all([
          userApi.getInfo(),
          userApi.getStats()
        ]);
        this.userInfo = userInfo;
        this.stats = stats;
      } catch (e) {
        console.error(e);
      }
    },
    
    getVipName(type) {
      const names = { 0: '免费用户', 1: '年卡会员', 2: '终身会员' };
      return names[type] || '免费用户';
    },
    
    goToSmsLogs() {
      uni.navigateTo({ url: '/pages/sms-logs/index' });
    },
    
    clearCache() {
      uni.showModal({
        title: '清理缓存',
        content: '确定要清理本地缓存吗？',
        success: (res) => {
          if (res.confirm) {
            uni.clearStorageSync();
            uni.showToast({ title: '清理成功', icon: 'success' });
          }
        }
      });
    },
    
    showAbout() {
      uni.showModal({
        title: '关于时光记',
        content: '时光记 - 记住每一个重要日子\n\n一款帮助您记住家人、朋友生日和纪念日的微信小程序。\n\n版本：1.0.0',
        showCancel: false
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

.content {
  padding: 24rpx;
}

.card {
  background: white;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 24rpx;
}

.user-section {
  display: flex;
  align-items: center;
}

.avatar {
  width: 100rpx;
  height: 100rpx;
  border-radius: 50%;
  background: #EEE;
  margin-right: 24rpx;
}

.user-detail {
  display: flex;
  flex-direction: column;
}

.nickname {
  font-size: 32rpx;
  font-weight: 600;
}

.user-type {
  font-size: 24rpx;
  color: #FFA500;
  margin-top: 8rpx;
}

.stats-title {
  font-size: 28rpx;
  font-weight: 600;
  margin-bottom: 24rpx;
}

.stats-grid {
  display: flex;
  justify-content: space-around;
}

.stat-item {
  text-align: center;
}

.stat-num {
  font-size: 40rpx;
  font-weight: 600;
  color: #4A90E2;
  display: block;
}

.stat-label {
  font-size: 24rpx;
  color: #999;
  margin-top: 8rpx;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 30rpx 0;
  border-bottom: 1rpx solid #EEE;
}

.menu-item:last-child {
  border-bottom: none;
}

.menu-icon {
  font-size: 36rpx;
  margin-right: 20rpx;
}

.menu-text {
  flex: 1;
  font-size: 30rpx;
}

.menu-arrow {
  color: #CCC;
  font-size: 28rpx;
}

.version-info {
  text-align: center;
  color: #CCC;
  font-size: 24rpx;
  padding: 40rpx 0;
}
</style>
