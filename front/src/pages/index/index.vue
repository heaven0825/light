<template>
  <view class="app">
    <!-- 顶部导航 -->
    <view class="nav-bar">
      <view class="nav-title">时光记</view>
      <view class="nav-slogan">记住每一个重要日子</view>
    </view>
    
    <!-- 主内容区 -->
    <view class="main-content">
      <!-- 即将到来 -->
      <view class="upcoming-section card">
        <view class="section-header">
          <text class="section-title">即将到来</text>
          <text class="more-link" @click="goToUpcoming">更多></text>
        </view>
        <view class="upcoming-list" v-if="upcomingList.length > 0">
          <view 
            class="upcoming-item" 
            v-for="item in upcomingList.slice(0, 5)" 
            :key="item.id"
            @click="goToDetail(item.id)"
          >
            <view class="upcoming-days" :class="{ 'today': item.days_until === 0 }">
              <text class="days-num">{{ item.days_until }}</text>
              <text class="days-text">天</text>
            </view>
            <view class="upcoming-info">
              <view class="upcoming-name">{{ item.name }}</view>
              <view class="upcoming-date">
                {{ item.lunar_display }}{{ item.month }}/{{ item.day }}
                <text v-if="item.age" class="age-text">{{ item.age }}岁</text>
              </view>
            </view>
            <view :class="['tag', getGroupTagClass(item.group_type)]">
              {{ getGroupName(item.group_type) }}
            </view>
          </view>
        </view>
        <view class="empty-mini" v-else>暂无即将到来的提醒</view>
      </view>
      
      <!-- 全部记录 -->
      <view class="records-section card">
        <view class="section-header">
          <text class="section-title">全部记录</text>
          <view class="header-actions">
            <text class="action-btn" @click="goToImport">导入</text>
            <text class="action-btn primary" @click="goToAdd">+ 添加</text>
          </view>
        </view>
        
        <!-- 分组筛选 -->
        <view class="filter-tabs">
          <view 
            v-for="tab in filterTabs" 
            :key="tab.value"
            :class="['filter-tab', { active: currentFilter === tab.value }]"
            @click="changeFilter(tab.value)"
          >{{ tab.label }}</view>
        </view>
        
        <!-- 记录列表 -->
        <view class="record-list">
          <view 
            class="record-card" 
            v-for="record in filteredRecords" 
            :key="record.id"
            @click="goToDetail(record.id)"
          >
            <view class="record-header">
              <text class="record-name">{{ record.name }}</text>
              <view :class="['tag', getGroupTagClass(record.group_type)]">
                {{ getGroupName(record.group_type) }}
              </view>
            </view>
            <view class="record-date">
              <text v-if="record.date_type === 2" class="lunar-tag">农历</text>
              {{ record.month }}月{{ record.day }}日
              <text v-if="record.year" class="age-tag">{{ calculateAge(record.year) }}岁</text>
            </view>
            <view class="record-actions">
              <text class="action-item" @click.stop="copyBlessing(record)">祝福语</text>
              <text class="action-item" @click.stop="goToSms(record)">发短信</text>
            </view>
          </view>
          
          <view class="empty-state" v-if="filteredRecords.length === 0">
            <text>暂无记录</text>
            <text class="empty-hint">点击右上角"添加"来创建第一条记录</text>
          </view>
        </view>
      </view>
    </view>
    
    <!-- 底部导航 -->
    <view class="tab-bar">
      <view class="tab-item active">
        <text class="tab-icon">🏠</text>
        <text class="tab-text">首页</text>
      </view>
      <view class="tab-item" @click="goToMember">
        <text class="tab-icon">👑</text>
        <text class="tab-text">会员</text>
      </view>
      <view class="tab-item" @click="goToSettings">
        <text class="tab-icon">⚙️</text>
        <text class="tab-text">设置</text>
      </view>
    </view>
  </view>
</template>

<script>
import { recordApi, blessingApi } from '../../api/index.js';

export default {
  data() {
    return {
      upcomingList: [],
      records: [],
      currentFilter: 0,
      filterTabs: [
        { label: '全部', value: 0 },
        { label: '家人', value: 1 },
        { label: '朋友', value: 2 },
        { label: '同事', value: 3 },
        { label: '客户', value: 4 }
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
  },
  
  onShow() {
    this.loadData();
  },
  
  methods: {
    async initLogin() {
      let openid = uni.getStorageSync('openid');
      if (!openid) {
        openid = 'mock_' + Date.now();
        uni.setStorageSync('openid', openid);
      }
    },
    
    async loadData() {
      try {
        const [upcoming, records] = await Promise.all([
          recordApi.getUpcoming(14),
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
    
    calculateAge(year) {
      return new Date().getFullYear() - year;
    },
    
    async copyBlessing(record) {
      try {
        const blessings = await blessingApi.getList(record.group_type);
        if (blessings.length > 0) {
          uni.setClipboardData({
            data: blessings[0].content,
            success: () => uni.showToast({ title: '已复制祝福语', icon: 'success' })
          });
        } else {
          uni.showToast({ title: '暂无祝福语', icon: 'none' });
        }
      } catch (e) {
        uni.showToast({ title: '获取失败', icon: 'none' });
      }
    },
    
    goToDetail(id) {
      uni.navigateTo({ url: '/pages/detail/index?id=' + id });
    },
    
    goToAdd() {
      uni.navigateTo({ url: '/pages/detail/index' });
    },
    
    goToImport() {
      uni.navigateTo({ url: '/pages/import/index' });
    },
    
    goToSms(record) {
      uni.navigateTo({ url: '/pages/sms/index?id=' + record.id + '&name=' + encodeURIComponent(record.name) });
    },
    
    goToUpcoming() {
      uni.navigateTo({ url: '/pages/upcoming/index' });
    },
    
    goToMember() {
      uni.switchTab({ url: '/pages/member/index' });
    },
    
    goToSettings() {
      uni.switchTab({ url: '/pages/settings/index' });
    }
  }
};
</script>

<style>
.app {
  min-height: 100vh;
  background: #F5F7FA;
  padding-bottom: 130rpx;
}

.nav-bar {
  background: linear-gradient(135deg, #4A90E2 0%, #667EE5 100%);
  color: white;
  padding: 60rpx 30rpx 120rpx;
}

.nav-title {
  font-size: 44rpx;
  font-weight: 600;
}

.nav-slogan {
  font-size: 26rpx;
  opacity: 0.9;
  margin-top: 8rpx;
}

.main-content {
  margin-top: -80rpx;
  padding: 0 24rpx;
}

.card {
  background: white;
  border-radius: 20rpx;
  padding: 30rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);
  margin-bottom: 24rpx;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: 600;
}

.more-link {
  color: #4A90E2;
  font-size: 26rpx;
}

.upcoming-list {
  display: flex;
  overflow-x: auto;
  gap: 20rpx;
  padding-bottom: 10rpx;
  -webkit-overflow-scrolling: touch;
}

.upcoming-item {
  flex-shrink: 0;
  width: 180rpx;
  text-align: center;
  padding: 20rpx;
  background: #F8F9FA;
  border-radius: 16rpx;
}

.upcoming-days {
  width: 100rpx;
  height: 100rpx;
  border-radius: 50%;
  background: #4A90E2;
  color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16rpx;
}

.upcoming-days.today {
  background: #FF6B6B;
}

.days-num {
  font-size: 36rpx;
  font-weight: 700;
}

.days-text {
  font-size: 20rpx;
}

.upcoming-name {
  font-size: 28rpx;
  font-weight: 500;
  margin-bottom: 6rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.upcoming-date {
  font-size: 22rpx;
  color: #999;
}

.age-text {
  margin-left: 6rpx;
  color: #4A90E2;
}

.header-actions {
  display: flex;
  gap: 24rpx;
}

.action-btn {
  color: #999;
  font-size: 26rpx;
}

.action-btn.primary {
  color: #4A90E2;
  font-weight: 500;
}

.filter-tabs {
  display: flex;
  gap: 12rpx;
  margin-bottom: 24rpx;
}

.filter-tab {
  padding: 10rpx 20rpx;
  border-radius: 30rpx;
  background: #F0F0F0;
  color: #666;
  font-size: 24rpx;
}

.filter-tab.active {
  background: #4A90E2;
  color: white;
}

.record-card {
  padding: 24rpx 0;
  border-bottom: 1rpx solid #EEE;
}

.record-card:last-child {
  border-bottom: none;
}

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10rpx;
}

.record-name {
  font-size: 30rpx;
  font-weight: 500;
}

.lunar-tag, .age-tag {
  background: #4A90E2;
  color: white;
  padding: 2rpx 10rpx;
  border-radius: 8rpx;
  font-size: 20rpx;
  margin-right: 10rpx;
}

.age-tag {
  background: #52C41A;
}

.record-date {
  font-size: 26rpx;
  color: #666;
  margin-bottom: 14rpx;
}

.record-actions {
  display: flex;
  gap: 32rpx;
}

.action-item {
  color: #4A90E2;
  font-size: 24rpx;
}

.tab-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  background: white;
  padding: 16rpx 0;
  box-shadow: 0 -4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.tab-item {
  flex: 1;
  text-align: center;
}

.tab-item.active .tab-icon,
.tab-item.active .tab-text {
  color: #4A90E2;
}

.tab-icon {
  display: block;
  font-size: 40rpx;
  margin-bottom: 4rpx;
}

.tab-text {
  font-size: 22rpx;
  color: #999;
}

.empty-mini {
  text-align: center;
  padding: 40rpx 0;
  color: #999;
  font-size: 26rpx;
}

.empty-hint {
  display: block;
  margin-top: 12rpx;
  color: #999;
  font-size: 24rpx;
}
</style>
