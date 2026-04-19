/**
 * 时光记 - API 配置与请求封装
 */

const API_BASE_URL = 'http://localhost:8000';

// 存储
const STORAGE_KEYS = {
  OPENID: 'light_openid',
  USER_INFO: 'light_user_info',
  TOKEN: 'light_token'
};

// 获取 openid
export function getOpenId() {
  return uni.getStorageSync(STORAGE_KEYS.OPENID) || '';
}

// 保存用户信息
export function setUserInfo(info) {
  uni.setStorageSync(STORAGE_KEYS.USER_INFO, info);
}

// 获取用户信息
export function getUserInfo() {
  return uni.getStorageSync(STORAGE_KEYS.USER_INFO) || null;
}

// 请求封装
async function request(url, method = 'GET', data = {}, params = {}) {
  const openid = getOpenId();
  
  // 构建 URL 参数
  const queryParams = { openid, ...params };
  const queryString = Object.entries(queryParams)
    .filter(([_, v]) => v !== undefined && v !== null && v !== '')
    .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
    .join('&');
  
  const fullUrl = `${API_BASE_URL}${url}${queryString ? '?' + queryString : ''}`;
  
  return new Promise((resolve, reject) => {
    uni.request({
      url: fullUrl,
      method,
      data,
      header: {
        'Content-Type': 'application/json'
      },
      success: (res) => {
        if (res.statusCode === 200) {
          resolve(res.data);
        } else if (res.statusCode === 401) {
          uni.showToast({ title: '请先登录', icon: 'none' });
          reject(res.data);
        } else if (res.statusCode === 400) {
          uni.showToast({ title: res.data.detail || '请求失败', icon: 'none' });
          reject(res.data);
        } else {
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

// 用户相关
export const userApi = {
  // 登录
  login: (openid, nickname, avatar) => {
    return request('/api/user/login', 'POST', { openid, nickname, avatar });
  },
  
  // 获取用户信息
  getInfo: () => {
    return request('/api/user/info');
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
    return request('/api/records/', 'GET', {}, params);
  },
  
  // 获取即将到来的记录
  getUpcoming: (days = 7) => {
    return request('/api/records/upcoming', 'GET', {}, { days });
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
    return request('/api/records/batch_import', 'POST', { items, group_type: groupType });
  }
};

// 祝福语相关
export const blessingApi = {
  // 获取祝福语列表
  getList: (groupType) => {
    return request('/api/blessings/', 'GET', {}, { group_type: groupType });
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
    return request('/api/order/create', 'POST', { pay_type: payType });
  },
  
  // 获取订单列表
  getList: () => {
    return request('/api/order/list', 'GET');
  },
  
  // 查询订单状态
  query: (orderNo) => {
    return request('/api/order/query', 'POST', { order_no: orderNo });
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
    return request('/api/sms/logs', 'GET', {}, { limit });
  },
  
  // 获取剩余条数
  getRemaining: () => {
    return request('/api/sms/remaining', 'GET');
  }
};

export default {
  getOpenId,
  setUserInfo,
  getUserInfo,
  userApi,
  recordApi,
  blessingApi,
  orderApi,
  smsApi
};
