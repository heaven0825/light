<template>
  <view class="app">
    <!-- 顶部导航 -->
    <view class="hero-section">
      <view class="hero-bg"></view>
      <view class="hero-content">
        <view class="app-logo">
          <text class="logo-icon">📅</text>
        </view>
        <view class="app-title">时光记</view>
        <view class="app-slogan">记住每一个重要日子</view>
        <view class="time-display">
          <view class="time-main">
            <text class="time-date">{{ currentDate }}</text>
            <text class="time-separator">|</text>
            <text class="time-clock">{{ currentTime }}</text>
          </view>
          <text class="time-lunar">{{ currentLunar }}</text>
        </view>
      </view>
      <view class="hero-decoration">
        <view class="deco-circle deco-1"></view>
        <view class="deco-circle deco-2"></view>
        <view class="deco-circle deco-3"></view>
      </view>
    </view>
    
    <!-- 主内容区 -->
    <view class="main-content">
      <!-- 即将到来 -->
      <view class="upcoming-section card">
        <view class="section-header">
          <view class="section-title-wrap">
            <text class="section-icon">🎁</text>
            <text class="section-title">即将到来</text>
            <text class="record-count" v-if="upcomingList.length > 0">{{ upcomingList.length }}个</text>
          </view>
        </view>
        <view class="upcoming-list" v-if="upcomingList.length > 0">
          <view 
            class="upcoming-item" 
            v-for="item in upcomingList.slice(0, 6)" 
            :key="item.id"
            @click="goToDetail(item.id)"
          >
            <view class="days-circle" :class="{ 'today': item.days_until === 0 }">
              <text class="days-num">{{ item.days_until }}</text>
              <text class="days-text">天</text>
            </view>
            <view class="upcoming-name">{{ item.name }}</view>
            <view class="upcoming-date">
              <text v-if="item.date_type === 2" class="lunar-badge">农历</text>
              {{ formatDate(item) }}
            </view>
            <view v-if="item.age" class="upcoming-age">{{ item.age }}岁</view>
            <view :class="['group-dot', getGroupDotClass(item.group_type)]"></view>
          </view>
        </view>
        <view class="empty-upcoming" v-else>
          <text class="empty-icon">🌸</text>
          <text class="empty-text">暂无即将到来的日子</text>
        </view>
      </view>
      
      <!-- 全部记录 -->
      <view class="records-section card">
        <view class="section-header">
          <view class="section-title-wrap">
            <text class="section-icon">📒</text>
            <text class="section-title">我的记录</text>
            <text class="record-count">{{ records.length }}条</text>
          </view>
        </view>
        <!-- 分组筛选 -->
        <scroll-view scroll-x class="filter-scroll">
          <view class="filter-tabs">
            <view 
              v-for="tab in filterTabs" 
              :key="tab.value"
              :class="['filter-tab', { active: currentFilter === tab.value }]"
              @click="changeFilter(tab.value)"
            >
              <text class="tab-icon">{{ getGroupIcon(tab.value) }}</text>
              <text class="tab-text">{{ tab.label }}</text>
            </view>
          </view>
        </scroll-view>
        
        <!-- 记录列表 -->
        <view class="record-list">
          <view 
            class="record-card" 
            v-for="record in filteredRecords" 
            :key="record.id"
            @click="goToDetail(record.id)"
          >
            <view class="record-left">
              <view class="record-avatar" :class="getAvatarClass(record.group_type)">
                {{ record.name.charAt(0) }}
              </view>
            </view>
            <view class="record-body">
              <view class="record-header">
                <text class="record-name">{{ record.name }}</text>
                <view :class="['tag', getGroupTagClass(record.group_type)]">
                  {{ getGroupName(record.group_type) }}
                </view>
              </view>
              <view class="record-date-row">
                <view class="date-main">
                  <text v-if="record.date_type === 2" class="lunar-badge small">农历</text>
                  {{ formatDate(record) }}
                </view>
                <text v-if="record.year" class="age-badge">{{ calculateAge(record.year) }}岁</text>
              </view>
            </view>
            <!-- 祝福语和短信功能已隐藏 -->
          </view>
          
          <view class="empty-state" v-if="filteredRecords.length === 0">
            <text class="empty-icon">📝</text>
            <text class="empty-main">暂无记录</text>
            <text class="empty-hint">点击右上角"添加"来创建第一条记录</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { authApi, recordApi, dateApi } from '../../api/index.js';

export default {
  data() {
    return {
      upcomingList: [],
      records: [],
      currentFilter: 0,
      currentDate: '',
      currentTime: '',
      currentLunar: '',
      timer: null,
      filterTabs: [
        { label: '全部', value: 0, icon: '📋' },
        { label: '家人', value: 1, icon: '👨‍👩‍👧' },
        { label: '朋友', value: 2, icon: '👫' },
        { label: '同事', value: 3, icon: '💼' },
        { label: '客户', value: 4, icon: '🤝' }
      ]
    };
  },
  
  computed: {
    filteredRecords() {
      if (this.currentFilter === 0) return this.records;
      return this.records.filter(r => r.group_type === this.currentFilter);
    }
  },
  
  onLoad() {
    this.initLogin();
    this.loadDateInfo();
    this.updateTime();
    this.timer = setInterval(this.updateTime, 1000);
  },
  
  onUnload() {
    if (this.timer) clearInterval(this.timer);
  },
  
  onShow() {
    this.loadData();
  },
  
  methods: {
    // 从后端加载日期信息（包含农历）
    async loadDateInfo() {
      try {
        const dateInfo = await dateApi.getNow();
        const lunar = dateInfo.lunar;
        this.currentLunar = `农历${lunar.month}${lunar.day}`;
      } catch (e) {
        console.error('获取日期信息失败:', e);
      }
    },
    
    // 更新阳历时间（每秒更新，分别显示日期和时间）
    updateTime() {
      const now = new Date();
      const month = String(now.getMonth() + 1).padStart(2, '0');
      const day = String(now.getDate()).padStart(2, '0');
      const hours = String(now.getHours()).padStart(2, '0');
      const minutes = String(now.getMinutes()).padStart(2, '0');
      const seconds = String(now.getSeconds()).padStart(2, '0');
      this.currentDate = `${month}月${day}日`;
      this.currentTime = `${hours}:${minutes}:${seconds}`;
    },
    
    async initLogin() {
      let token = uni.getStorageSync('token');
      if (!token) {
        try {
          const loginRes = await new Promise((resolve, reject) => {
            uni.login({
              provider: 'weixin',
              success: resolve,
              fail: reject
            });
          });
          
          if (loginRes.code) {
            const data = await authApi.login(loginRes.code);
            uni.setStorageSync('token', data.token);
            uni.setStorageSync('openid', data.openid);
            uni.setStorageSync('user_info', data.user);
            console.log('登录成功 openid:', data.openid);
            // 登录成功后加载数据
            this.loadData();
          }
        } catch (e) {
          console.error('登录失败:', e);
        }
      } else {
        // 已登录，加载数据
        this.loadData();
      }
    },
    
    async loadData() {
      try {
        const [upcoming, records] = await Promise.all([
          recordApi.getList({ days: 14 }),
          recordApi.getList()
        ]);
        this.upcomingList = upcoming || [];
        this.records = records || [];
      } catch (e) {
        console.error('加载失败', e);
      }
    },
    
    changeFilter(type) {
      this.currentFilter = type;
    },
    
    getGroupName(type) {
      const names = { 1: '家人', 2: '朋友', 3: '同事', 4: '客户' };
      return names[type] || '其他';
    },
    
    getGroupTagClass(type) {
      const classes = { 1: 'tag-family', 2: 'tag-friend', 3: 'tag-colleague', 4: 'tag-client' };
      return classes[type] || '';
    },
    
    getGroupDotClass(type) {
      const classes = { 1: 'dot-family', 2: 'dot-friend', 3: 'dot-colleague', 4: 'dot-client' };
      return classes[type] || '';
    },
    
    getGroupIcon(type) {
      const icons = { 0: '📋', 1: '👨‍👩‍👧', 2: '👫', 3: '💼', 4: '🤝' };
      return icons[type] || '📋';
    },
    
    getAvatarClass(type) {
      const classes = { 1: 'avatar-family', 2: 'avatar-friend', 3: 'avatar-colleague', 4: 'avatar-client' };
      return classes[type] || '';
    },
    
    calculateAge(year) {
      return new Date().getFullYear() - year;
    },
    
    formatDate(item) {
      if (item.date_type === 2) {
        // 农历日期
        return item.lunar_month_text + item.lunar_day_text;
      } else {
        // 公历日期：X月Y日
        return item.month + '月' + item.day + '日';
      }
    },
    
    goToDetail(id) {
      uni.navigateTo({ url: '/pages/detail/index?id=' + id });
    }
  }
};
</script>

<style>
.app {
  min-height: 100vh;
  background: linear-gradient(180deg, #FFF8F9 0%, #FFF0F5 100%);
}

/* 顶部英雄区 */
.hero-section {
  position: relative;
  background: linear-gradient(135deg, #FFE4E1 0%, #FFC0CB 50%, #FFB6C1 100%);
  padding: 80rpx 40rpx 140rpx;
  overflow: hidden;
  border-radius: 0 0 50rpx 50rpx;
}

.hero-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}

.hero-content {
  position: relative;
  z-index: 1;
  text-align: center;
  color: white;
}

.app-logo {
  width: 100rpx;
  height: 100rpx;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 25rpx;
  margin: 0 auto 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.08);
}

.logo-icon {
  font-size: 60rpx;
}

.app-title {
  font-size: 44rpx;
  font-weight: 600;
  color: #8B4513;
  letter-spacing: 2rpx;
  margin-bottom: 6rpx;
}

.app-slogan {
  font-size: 24rpx;
  color: #A0522D;
  margin-bottom: 32rpx;
}

.time-display {
  background: rgba(255, 255, 255, 0.7);
  border-radius: 16rpx;
  padding: 20rpx 28rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.06);
}

.time-main {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16rpx;
  margin-bottom: 8rpx;
}

.time-date {
  font-size: 28rpx;
  color: #8B4513;
  font-weight: 500;
}

.time-separator {
  color: #DEB887;
  font-size: 22rpx;
  margin: 0 12rpx;
}

.time-clock {
  font-size: 36rpx;
  font-weight: 600;
  color: #8B4513;
  font-family: 'DIN Alternate', -apple-system, sans-serif;
  letter-spacing: 2rpx;
}

.time-lunar {
  font-size: 22rpx;
  color: #A0522D;
  margin-top: 6rpx;
}

/* 装饰元素 */
.hero-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.deco-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
}

.deco-1 {
  width: 200rpx;
  height: 200rpx;
  top: -60rpx;
  right: -40rpx;
}

.deco-2 {
  width: 120rpx;
  height: 120rpx;
  top: 120rpx;
  left: -30rpx;
}

.deco-3 {
  width: 80rpx;
  height: 80rpx;
  bottom: 60rpx;
  right: 100rpx;
}

/* 主内容区 */
.main-content {
  margin-top: -80rpx;
  padding: 0 24rpx 40rpx;
  position: relative;
  z-index: 2;
}

.card {
  background: white;
  border-radius: 24rpx;
  padding: 28rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);
  margin-bottom: 24rpx;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28rpx;
}

.section-title-wrap {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.section-icon {
  font-size: 32rpx;
}

.section-title {
  font-size: 34rpx;
  font-weight: 600;
  color: #333;
}

.record-count {
  font-size: 24rpx;
  color: #999;
  background: #F5F5F5;
  padding: 4rpx 16rpx;
  border-radius: 20rpx;
  margin-left: 8rpx;
}

.more-link {
  display: flex;
  align-items: center;
  gap: 4rpx;
  color: #FF6A88;
  font-size: 26rpx;
}

.arrow {
  font-size: 32rpx;
  font-weight: bold;
}

/* 即将到来区域 */
.upcoming-list {
  display: flex;
  overflow-x: auto;
  gap: 20rpx;
  padding: 8rpx 0 16rpx;
  -webkit-overflow-scrolling: touch;
}

.upcoming-list::-webkit-scrollbar {
  display: none;
}

.upcoming-item {
  flex-shrink: 0;
  width: 150rpx;
  text-align: center;
  padding: 24rpx 14rpx;
  background: linear-gradient(180deg, #FFF8F9 0%, #FFF0F3 100%);
  border-radius: 20rpx;
  position: relative;
  border: 1rpx solid #FFE4E8;
  transition: all 0.3s ease;
}

.upcoming-item:active {
  transform: scale(0.96);
  border-color: #FFB7C5;
}

.days-circle {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #FFB6C1, #FFC0CB);
  color: #8B4513;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12rpx;
  box-shadow: 0 4rpx 12rpx rgba(255, 183, 193, 0.4);
}

.days-circle.today {
  background: linear-gradient(135deg, #FF69B4, #FFB6C1);
  color: white;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.days-num {
  font-size: 32rpx;
  font-weight: 600;
}

.days-text {
  font-size: 16rpx;
}

.upcoming-name {
  font-size: 26rpx;
  font-weight: 500;
  color: #5C4033;
  margin-bottom: 4rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.upcoming-date {
  font-size: 20rpx;
  color: #A0522D;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4rpx;
}

.upcoming-age {
  font-size: 18rpx;
  color: #FF69B4;
  margin-top: 4rpx;
}

.lunar-badge {
  background: linear-gradient(135deg, #FFB6C1, #FFC0CB);
  color: #8B4513;
  padding: 2rpx 8rpx;
  border-radius: 6rpx;
  font-size: 16rpx;
  margin-right: 4rpx;
}

.lunar-badge.small {
  padding: 1rpx 6rpx;
  font-size: 16rpx;
}

.group-dot {
  position: absolute;
  top: 16rpx;
  right: 16rpx;
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;
}

.dot-family { background: #FFB6C1; }
.dot-friend { background: #DDA0DD; }
.dot-colleague { background: #C9A0DC; }
.dot-client { background: #E8B4D8; }

.empty-upcoming {
  text-align: center;
  padding: 48rpx 0;
}

.empty-icon {
  font-size: 64rpx;
  display: block;
  margin-bottom: 16rpx;
}

.empty-text {
  color: #999;
  font-size: 26rpx;
}

/* 头部操作按钮 */
.header-actions {
  display: flex;
  gap: 16rpx;
}

.action-btn-import {
  padding: 14rpx 24rpx;
  border-radius: 30rpx;
  background: #FFF5F3;
  color: #FF6A88;
  font-size: 26rpx;
  font-weight: 500;
}

.action-btn-add {
  display: flex;
  align-items: center;
  gap: 4rpx;
  padding: 14rpx 28rpx;
  border-radius: 30rpx;
  background: linear-gradient(135deg, #FF9A8B, #FF6A88);
  color: white;
  font-size: 26rpx;
  font-weight: 500;
  box-shadow: 0 6rpx 20rpx rgba(255, 107, 136, 0.3);
}

.add-icon {
  font-size: 32rpx;
  font-weight: bold;
  line-height: 1;
}

/* 筛选标签 */
.filter-scroll {
  white-space: nowrap;
  margin: 0 -28rpx 20rpx;
  padding: 0 28rpx;
}

.filter-tabs {
  display: inline-flex;
  gap: 14rpx;
}

.filter-tab {
  display: flex;
  align-items: center;
  gap: 6rpx;
  padding: 12rpx 20rpx;
  border-radius: 25rpx;
  background: #FFF5F7;
  color: #A0522D;
  font-size: 24rpx;
  white-space: nowrap;
  transition: all 0.3s ease;
}

.filter-tab.active {
  background: linear-gradient(135deg, #FFB6C1, #FFC0CB);
  color: #8B4513;
  box-shadow: 0 4rpx 12rpx rgba(255, 183, 193, 0.4);
}

.tab-icon {
  font-size: 24rpx;
}

/* 记录列表 */
.record-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.record-card {
  display: flex;
  align-items: center;
  padding: 22rpx;
  background: linear-gradient(180deg, #FFFDFE 0%, #FFF8F9 100%);
  border-radius: 20rpx;
  border: 1rpx solid #FFE4E8;
  transition: all 0.3s ease;
}

.record-card:active {
  transform: scale(0.98);
  border-color: #FFB6C1;
}

.record-left {
  margin-right: 18rpx;
}

.record-avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32rpx;
  font-weight: 600;
  color: white;
}

.avatar-family { background: linear-gradient(135deg, #FFB6C1, #FFA0B4); }
.avatar-friend { background: linear-gradient(135deg, #E8B4D8, #DDA0DD); }
.avatar-colleague { background: linear-gradient(135deg, #C9A0DC, #BA8EC9); }
.avatar-client { background: linear-gradient(135deg, #DDA0DD, #DA70D6); }

.record-body {
  flex: 1;
  min-width: 0;
}

.record-header {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 8rpx;
}

.record-name {
  font-size: 28rpx;
  font-weight: 500;
  color: #5C4033;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tag {
  padding: 4rpx 10rpx;
  border-radius: 10rpx;
  font-size: 18rpx;
  color: white;
  flex-shrink: 0;
}

.tag-family { background: #FFB6C1; }
.tag-friend { background: #DDA0DD; }
.tag-colleague { background: #C9A0DC; }
.tag-client { background: #E8B4D8; }

.record-date-row {
  display: flex;
  align-items: center;
  gap: 10rpx;
}

.date-main {
  display: flex;
  align-items: center;
  gap: 4rpx;
  font-size: 24rpx;
  color: #A0522D;
}

.age-badge {
  background: linear-gradient(135deg, #FFF5F7, #FFE4E8);
  color: #FF69B4;
  padding: 4rpx 10rpx;
  border-radius: 10rpx;
  font-size: 20rpx;
  font-weight: 500;
}

.record-actions {
  display: flex;
  gap: 16rpx;
  margin-left: 16rpx;
}

.action-icon {
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  background: #FFF5F3;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
  transition: all 0.2s ease;
}

.action-icon:active {
  transform: scale(0.9);
  background: #FFE8E3;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 60rpx 0;
}

.empty-icon {
  font-size: 80rpx;
  display: block;
  margin-bottom: 20rpx;
}

.empty-main {
  font-size: 30rpx;
  color: #666;
  margin-bottom: 12rpx;
}

.empty-hint {
  color: #999;
  font-size: 24rpx;
}
</style>
