/**
 * 时光记 - API 配置与请求封装 (RESTful)
 */

const API_BASE_URL = 'http://localhost:8000';

const STORAGE_KEYS = {
  OPENID: 'openid',
  TOKEN: 'token',
  USER_INFO: 'user_info'
};

// 获取 token
function getToken() {
  return uni.getStorageSync(STORAGE_KEYS.TOKEN) || '';
}

// 获取 openid
function getOpenId() {
  return uni.getStorageSync(STORAGE_KEYS.OPENID) || '';
}

// 保存登录信息
function setLoginInfo(data) {
  uni.setStorageSync(STORAGE_KEYS.TOKEN, data.token);
  uni.setStorageSync(STORAGE_KEYS.OPENID, data.openid);
  uni.setStorageSync(STORAGE_KEYS.USER_INFO, data.user);
}

// 获取用户信息
function getUserInfo() {
  return uni.getStorageSync(STORAGE_KEYS.USER_INFO) || null;
}

// 请求封装
async function request(url, method = 'GET', data = {}) {
  const token = getToken();
  
  return new Promise((resolve, reject) => {
    uni.request({
      url: `${API_BASE_URL}${url}`,
      method,
      data,
      header: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : ''
      },
      success: (res) => {
        if (res.statusCode === 200) {
          const response = res.data;
          // RESTful 统一响应格式
          if (response.code === 200) {
            resolve(response.data);
          } else {
            uni.showToast({ title: response.message || '请求失败', icon: 'none' });
            reject(response);
          }
        } else if (res.statusCode === 401) {
          uni.showToast({ title: '请先登录', icon: 'none' });
          uni.removeStorageSync(STORAGE_KEYS.TOKEN);
          reject(res.data);
        } else {
          uni.showToast({ title: res.data.message || '请求失败', icon: 'none' });
          reject(res.data);
        }
      },
      fail: (err) => {
        uni.showToast({ title: '网络请求失败', icon: 'none' });
        reject(err);
      }
    });
  });
}

// ============ API 接口 ============

// 认证相关
export const authApi = {
  // 微信登录
  login: (code) => {
    return request('/api/auth/login', 'POST', { code });
  }
};

// 用户相关
export const userApi = {
  // 获取当前用户信息
  getInfo: () => {
    return request('/api/user/me');
  },
  
  // 更新用户信息
  updateInfo: (data) => {
    return request('/api/user/me', 'PUT', data);
  },
  
  // 获取用户统计
  getStats: () => {
    return request('/api/user/stats');
  }
};

// 记录相关
export const recordApi = {
  // 获取记录列表
  getList: (params = {}) => {
    return request('/api/records/', 'GET', params);
  },
  
  // 获取单条记录
  getOne: (id) => {
    return request(`/api/records/${id}`, 'GET');
  },
  
  // 创建记录
  create: (data) => {
    return request('/api/records/', 'POST', data);
  },
  
  // 更新记录
  update: (id, data) => {
    return request(`/api/records/${id}`, 'PUT', data);
  },
  
  // 删除记录
  delete: (id) => {
    return request(`/api/records/${id}`, 'DELETE');
  },
  
  // 批量导入
  batchImport: (items, groupType = 1) => {
    return request('/api/records/batch', 'POST', { items, group_type: groupType });
  }
};

// 祝福语相关
export const blessingApi = {
  // 获取祝福语列表
  getList: (groupType) => {
    return request('/api/blessings/', 'GET', { group_type: groupType });
  },
  
  // 获取所有祝福语
  getAll: () => {
    return request('/api/blessings/all', 'GET');
  }
};

// 订单相关
export const orderApi = {
  // 创建订单
  create: (payType) => {
    return request('/api/orders/', 'POST', { pay_type: payType });
  },
  
  // 获取订单列表
  getList: () => {
    return request('/api/orders/', 'GET');
  },
  
  // 模拟支付
  pay: (orderNo) => {
    return request('/api/orders/pay', 'POST', { order_no: orderNo });
  }
};

// 短信相关
export const smsApi = {
  // 发送短信
  send: (data) => {
    return request('/api/sms/send', 'POST', data);
  },
  
  // 获取发送记录
  getLogs: (limit = 20) => {
    return request('/api/sms/logs', 'GET', { limit });
  },
  
  // 获取剩余条数
  getRemaining: () => {
    return request('/api/sms/remaining', 'GET');
  }
};

// 日期相关
export const dateApi = {
  // 获取当前日期信息（包含农历）
  getNow: () => {
    return request('/api/date/now', 'GET');
  }
};

export default {
  getOpenId,
  getUserInfo,
  setLoginInfo,
  authApi,
  userApi,
  recordApi,
  blessingApi,
  orderApi,
  smsApi,
  dateApi
};
