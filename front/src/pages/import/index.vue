<template>
  <view class="page">
    <view class="nav-bar">
      <text class="nav-title">批量导入</text>
    </view>
    
    <view class="content">
      <!-- 说明 -->
      <view class="tips-section">
        <view class="tips-title">格式说明</view>
        <view class="tips-content">
          <text>每行一条，格式：日期 姓名</text>
          <text class="tip-item">公历：0408 家人 / 1204 朋友</text>
          <text class="tip-item">农历：正月十五 家人 / 七月廿二 朋友</text>
          <text class="tip-item">可在姓名后加 @家人/@朋友/@同事/@客户 指定分组</text>
        </view>
      </view>
      
      <!-- 分组选择 -->
      <view class="form-section">
        <view class="form-label">默认分组</view>
        <picker mode="selector" :range="groupOptions" range-key="label" @change="changeGroup">
          <view class="picker-value">{{ getGroupLabel(defaultGroup) }}</view>
        </picker>
      </view>
      
      <!-- 文本输入 -->
      <view class="form-section text-section">
        <view class="form-label">导入内容</view>
        <textarea 
          class="text-input" 
          v-model="importText" 
          placeholder="例如：
0408 妈妈
正月十五 爸爸
1204 张三@朋友
七月廿二 李四@同事"
          :maxlength="-1"
        ></textarea>
      </view>
      
      <!-- 预览 -->
      <view class="preview-section" v-if="parsedItems.length > 0">
        <view class="preview-title">预览 ({{ parsedItems.length }}条)</view>
        <view class="preview-list">
          <view class="preview-item" v-for="(item, index) in parsedItems" :key="index">
            <text class="preview-date">{{ item.displayDate }}</text>
            <text class="preview-name">{{ item.name }}</text>
            <text class="preview-group">{{ getGroupLabel(item.group_type) }}</text>
          </view>
        </view>
      </view>
      
      <!-- 按钮 -->
      <button class="btn-save" @click="startImport" :disabled="loading || parsedItems.length === 0">
        {{ loading ? '导入中...' : '开始导入' }}
      </button>
    </view>
  </view>
</template>

<script>
import { recordApi } from '../../api/index.js';

export default {
  data() {
    return {
      importText: '',
      defaultGroup: 1,
      groupOptions: [
        { label: '家人', value: 1 },
        { label: '朋友', value: 2 },
        { label: '同事', value: 3 },
        { label: '客户', value: 4 }
      ],
      loading: false
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
        let groupType = this.defaultGroup;
        let isLunar = false;
        
        // 检查姓名后是否带分组
        if (name.includes('@')) {
          const [realName, groupStr] = name.split('@');
          name = realName;
          groupType = groupMap[groupStr] || this.defaultGroup;
        }
        
        // 解析日期
        if (dateStr.includes('月') || dateStr.includes('初') || dateStr.includes('廿')) {
          isLunar = true;
          // 农历日期解析
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
            displayDate: `农历${month}/${day}`
          });
        } else if (/^\d{4}$/.test(dateStr)) {
          // 公历日期 0408
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
    changeGroup(e) {
      this.defaultGroup = this.groupOptions[e.detail.value].value;
    },
    
    getGroupLabel(type) {
      const names = { 1: '家人', 2: '朋友', 3: '同事', 4: '客户' };
      return names[type] || '其他';
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
        
        const result = await recordApi.batchImport(items, this.defaultGroup);
        
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

.tips-section {
  background: #E6F7FF;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 24rpx;
}

.tips-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #1890FF;
  margin-bottom: 12rpx;
}

.tips-content {
  font-size: 24rpx;
  color: #666;
  line-height: 1.8;
}

.tip-item {
  display: block;
  margin-top: 6rpx;
}

.form-section {
  background: white;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 20rpx;
}

.form-label {
  font-size: 26rpx;
  color: #999;
  margin-bottom: 12rpx;
}

.picker-value {
  font-size: 30rpx;
}

.text-section {
  min-height: 300rpx;
}

.text-input {
  width: 100%;
  min-height: 250rpx;
  font-size: 28rpx;
  line-height: 1.8;
}

.preview-section {
  background: white;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 24rpx;
}

.preview-title {
  font-size: 26rpx;
  color: #999;
  margin-bottom: 16rpx;
}

.preview-item {
  display: flex;
  align-items: center;
  padding: 16rpx 0;
  border-bottom: 1rpx solid #EEE;
}

.preview-item:last-child {
  border-bottom: none;
}

.preview-date {
  width: 120rpx;
  font-size: 26rpx;
  color: #4A90E2;
}

.preview-name {
  flex: 1;
  font-size: 28rpx;
}

.preview-group {
  font-size: 22rpx;
  color: #999;
}

.btn-save {
  width: 100%;
  background: linear-gradient(135deg, #4A90E2, #667EE5);
  color: white;
  border-radius: 44rpx;
  padding: 28rpx;
  font-size: 32rpx;
  border: none;
}
</style>
