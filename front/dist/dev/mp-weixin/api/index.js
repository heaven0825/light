"use strict";
const common_vendor = require("../common/vendor.js");
const API_BASE_URL = "http://localhost:8000";
const STORAGE_KEYS = {
  TOKEN: "token"
};
function getToken() {
  return common_vendor.index.getStorageSync(STORAGE_KEYS.TOKEN) || "";
}
async function request(url, method = "GET", data = {}) {
  const token = getToken();
  return new Promise((resolve, reject) => {
    common_vendor.index.request({
      url: `${API_BASE_URL}${url}`,
      method,
      data,
      header: {
        "Content-Type": "application/json",
        "Authorization": token ? `Bearer ${token}` : ""
      },
      success: (res) => {
        if (res.statusCode === 200) {
          const response = res.data;
          if (response.code === 200) {
            resolve(response.data);
          } else {
            common_vendor.index.showToast({ title: response.message || "请求失败", icon: "none" });
            reject(response);
          }
        } else if (res.statusCode === 401) {
          common_vendor.index.showToast({ title: "请先登录", icon: "none" });
          common_vendor.index.removeStorageSync(STORAGE_KEYS.TOKEN);
          reject(res.data);
        } else {
          common_vendor.index.showToast({ title: res.data.message || "请求失败", icon: "none" });
          reject(res.data);
        }
      },
      fail: (err) => {
        common_vendor.index.showToast({ title: "网络请求失败", icon: "none" });
        reject(err);
      }
    });
  });
}
const authApi = {
  // 微信登录
  login: (code) => {
    return request("/api/auth/login", "POST", { code });
  }
};
const userApi = {
  // 获取当前用户信息
  getInfo: () => {
    return request("/api/user/me");
  },
  // 更新用户信息
  updateInfo: (data) => {
    return request("/api/user/me", "PUT", data);
  },
  // 获取用户统计
  getStats: () => {
    return request("/api/user/stats");
  }
};
const recordApi = {
  // 获取记录列表
  getList: (params = {}) => {
    return request("/api/records/", "GET", params);
  },
  // 获取单条记录
  getOne: (id) => {
    return request(`/api/records/${id}`, "GET");
  },
  // 创建记录
  create: (data) => {
    return request("/api/records/", "POST", data);
  },
  // 更新记录
  update: (id, data) => {
    return request(`/api/records/${id}`, "PUT", data);
  },
  // 删除记录
  delete: (id) => {
    return request(`/api/records/${id}`, "DELETE");
  },
  // 批量导入
  batchImport: (items, groupType = 1) => {
    return request("/api/records/batch", "POST", { items, group_type: groupType });
  }
};
const blessingApi = {
  // 获取祝福语列表
  getList: (groupType) => {
    return request("/api/blessings/", "GET", { group_type: groupType });
  },
  // 获取所有祝福语
  getAll: () => {
    return request("/api/blessings/all", "GET");
  }
};
const orderApi = {
  // 创建订单
  create: (payType) => {
    return request("/api/orders/", "POST", { pay_type: payType });
  },
  // 获取订单列表
  getList: () => {
    return request("/api/orders/", "GET");
  },
  // 模拟支付
  pay: (orderNo) => {
    return request("/api/orders/pay", "POST", { order_no: orderNo });
  }
};
const smsApi = {
  // 发送短信
  send: (data) => {
    return request("/api/sms/send", "POST", data);
  },
  // 获取发送记录
  getLogs: (limit = 20) => {
    return request("/api/sms/logs", "GET", { limit });
  },
  // 获取剩余条数
  getRemaining: () => {
    return request("/api/sms/remaining", "GET");
  }
};
const dateApi = {
  // 获取当前日期信息（包含农历）
  getNow: () => {
    return request("/api/date/now", "GET");
  }
};
exports.authApi = authApi;
exports.blessingApi = blessingApi;
exports.dateApi = dateApi;
exports.orderApi = orderApi;
exports.recordApi = recordApi;
exports.smsApi = smsApi;
exports.userApi = userApi;
