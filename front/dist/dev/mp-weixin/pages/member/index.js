"use strict";
const common_vendor = require("../../common/vendor.js");
const api_index = require("../../api/index.js");
const _sfc_main = {
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
        this.userInfo = await api_index.userApi.getInfo();
      } catch (e) {
        console.error(e);
      }
    },
    getVipName(type) {
      const names = { 0: "免费用户", 1: "年卡会员", 2: "终身会员" };
      return names[type] || "免费用户";
    },
    async buyVip(payType) {
      try {
        const order = await api_index.orderApi.create(payType);
        common_vendor.index.showModal({
          title: "模拟支付",
          content: `订单号: ${order.order_no}
金额: ¥${order.amount}`,
          success: async (res) => {
            if (res.confirm) {
              await common_vendor.index.request({
                url: `http://localhost:/api/order/pay/callback?order_no=${order.order_no}`,
                method: "POST"
              });
              common_vendor.index.showToast({ title: "支付成功", icon: "success" });
              this.loadUserInfo();
            }
          }
        });
      } catch (e) {
        common_vendor.index.showToast({ title: e.detail || "创建订单失败", icon: "none" });
      }
    }
  }
};
function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
  return common_vendor.e({
    a: $data.userInfo && $data.userInfo.vip_type > 0
  }, $data.userInfo && $data.userInfo.vip_type > 0 ? common_vendor.e({
    b: common_vendor.t($options.getVipName($data.userInfo.vip_type)),
    c: $data.userInfo.vip_type === 1
  }, $data.userInfo.vip_type === 1 ? {
    d: common_vendor.t($data.userInfo.vip_expire_time)
  } : {}) : {}, {
    e: common_vendor.o(($event) => $options.buyVip(1), "4a"),
    f: common_vendor.o(($event) => $options.buyVip(2), "13")
  });
}
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["render", _sfc_render], ["__scopeId", "data-v-97d9768f"]]);
wx.createPage(MiniProgramPage);
