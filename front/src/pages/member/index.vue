<template>
  <view class="page">
    <view class="nav-bar">
      <text class="nav-title">会员中心</text>
    </view>
    
    <view class="content">
      <!-- 当前状态 -->
      <view class="current-vip" v-if="userInfo && userInfo.vip_type > 0">
        <view class="vip-badge">
          <text class="vip-icon">👑</text>
          <text class="vip-name">{{ getVipName(userInfo.vip_type) }}</text>
        </view>
        <view class="vip-expire" v-if="userInfo.vip_type === 1">
          到期时间：{{ userInfo.vip_expire_time }}
        </view>
        <view class="vip-permanent" v-else>永久有效</view>
      </view>
      
      <!-- 免费用户 -->
      <view class="free-user" v-else>
        <text class="free-icon">🌱</text>
        <text class="free-text">免费用户</text>
        <text class="free-hint">升级会员解锁更多功能</text>
      </view>
      
      <!-- 功能对比 -->
      <view class="compare-section">
        <view class="section-title">会员特权</view>
        <view class="compare-table">
          <view class="compare-row header">
            <view class="compare-col">功能</view>
            <view class="compare-col">免费</view>
            <view class="compare-col">年卡</view>
            <view class="compare-col">终身</view>
          </view>
          <view class="compare-row">
            <view class="compare-col">记录条数</view>
            <view class="compare-col">8条</view>
            <view class="compare-col">100条</view>
            <view class="compare-col">100条</view>
          </view>
          <view class="compare-row">
            <view class="compare-col">祝福语</view>
            <view class="compare-col">每组3条</view>
            <view class="compare-col">无限</view>
            <view class="compare-col">无限</view>
          </view>
          <view class="compare-row">
            <view class="compare-col">短信提醒</view>
            <view class="compare-col">3条</view>
            <view class="compare-col">无限</view>
            <view class="compare-col">无限</view>
          </view>
          <view class="compare-row">
            <view class="compare-col">自动年重复</view>
            <view class="compare-col">-</view>
            <view class="compare-col">✓</view>
            <view class="compare-col">✓</view>
          </view>
        </view>
      </view>
      
      <!-- 购买按钮 -->
      <view class="buy-section">
        <view class="buy-card" @click="buyVip(1)">
          <view class="buy-info">
            <text class="buy-name">年卡会员</text>
            <text class="buy-price">¥9.9 <text class="buy-period">/年</text></text>
          </view>
          <text class="buy-btn">立即开通</text>
        </view>
        
        <view class="buy-card recommended" @click="buyVip(2)">
          <view class="recommended-tag">推荐</view>
          <view class="buy-info">
            <text class="buy-name">终身会员</text>
            <text class="buy-price">¥39.9 <text class="buy-period">/永久</text></text>
          </view>
          <text class="buy-btn">立即开通</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { userApi, orderApi } from '../../api/index.js';

export default {
  data() {
    return {
      userInfo: null
    };
  },
  
  onLoad() {
    this.loadUserInfo();
  },
  
  methods: {
    async loadUserInfo() {
      try {
        this.userInfo = await userApi.getInfo();
      } catch (e) {
        console.error(e);
      }
    },
    
    getVipName(type) {
      const names = { 0: '免费用户', 1: '年卡会员', 2: '终身会员' };
      return names[type] || '免费用户';
    },
    
    async buyVip(payType) {
      try {
        const order = await orderApi.create(payType);
        // 实际应用中这里会调用微信支付
        uni.showModal({
          title: '模拟支付',
          content: `订单号: ${order.order_no}\n金额: ¥${order.amount}`,
          success: async (res) => {
            if (res.confirm) {
              // 模拟支付回调
              await uni.request({
                url: `http://localhost:8000/api/order/pay/callback?order_no=${order.order_no}`,
                method: 'POST'
              });
              uni.showToast({ title: '支付成功', icon: 'success' });
              this.loadUserInfo();
            }
          }
        });
      } catch (e) {
        uni.showToast({ title: e.detail || '创建订单失败', icon: 'none' });
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
  background: linear-gradient(135deg, #4A90E2, #667EE5);
  color: white;
  padding: 60rpx 30rpx 120rpx;
  text-align: center;
}

.nav-title {
  font-size: 34rpx;
  font-weight: 600;
}

.content {
  padding: 24rpx;
  margin-top: -80rpx;
}

.current-vip, .free-user {
  background: linear-gradient(135deg, #FFD700, #FFA500);
  border-radius: 20rpx;
  padding: 40rpx;
  text-align: center;
  color: white;
  margin-bottom: 24rpx;
}

.vip-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  margin-bottom: 16rpx;
}

.vip-icon {
  font-size: 48rpx;
}

.vip-name {
  font-size: 36rpx;
  font-weight: 600;
}

.vip-expire, .vip-permanent {
  font-size: 26rpx;
  opacity: 0.9;
}

.free-user {
  background: linear-gradient(135deg, #52C41A, #73D13D);
}

.free-icon {
  font-size: 60rpx;
  display: block;
  margin-bottom: 12rpx;
}

.free-text {
  font-size: 32rpx;
  font-weight: 600;
}

.free-hint {
  font-size: 24rpx;
  opacity: 0.9;
  display: block;
  margin-top: 8rpx;
}

.compare-section {
  background: white;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 24rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: 600;
  margin-bottom: 24rpx;
}

.compare-table {
  font-size: 24rpx;
}

.compare-row {
  display: flex;
  border-bottom: 1rpx solid #EEE;
  padding: 20rpx 0;
}

.compare-row.header {
  background: #F8F9FA;
  border-radius: 8rpx;
  font-weight: 600;
}

.compare-col {
  flex: 1;
  text-align: center;
}

.buy-section {
  display: flex;
  gap: 20rpx;
}

.buy-card {
  flex: 1;
  background: white;
  border-radius: 20rpx;
  padding: 30rpx;
  position: relative;
}

.buy-card.recommended {
  border: 2rpx solid #4A90E2;
}

.recommended-tag {
  position: absolute;
  top: -10rpx;
  right: 20rpx;
  background: #4A90E2;
  color: white;
  padding: 4rpx 16rpx;
  border-radius: 20rpx;
  font-size: 20rpx;
}

.buy-info {
  text-align: center;
  margin-bottom: 20rpx;
}

.buy-name {
  font-size: 28rpx;
  display: block;
  margin-bottom: 8rpx;
}

.buy-price {
  font-size: 36rpx;
  font-weight: 600;
  color: #FF6B6B;
}

.buy-period {
  font-size: 24rpx;
  color: #999;
  font-weight: normal;
}

.buy-btn {
  width: 100%;
  background: linear-gradient(135deg, #4A90E2, #667EE5);
  color: white;
  padding: 20rpx;
  border-radius: 30rpx;
  text-align: center;
  font-size: 28rpx;
}
</style>
