"use strict";
const common_vendor = require("../../common/vendor.js");
const api_index = require("../../api/index.js");
const _sfc_main = {
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
          api_index.userApi.getInfo(),
          api_index.userApi.getStats()
        ]);
        this.userInfo = userInfo;
        this.stats = stats;
      } catch (e) {
        console.error(e);
      }
    },
    getVipName(type) {
      const names = { 0: "免费用户", 1: "年卡会员", 2: "终身会员" };
      return names[type] || "免费用户";
    },
    goToSmsLogs() {
      common_vendor.index.navigateTo({ url: "/pages/sms-logs/index" });
    },
    clearCache() {
      common_vendor.index.showModal({
        title: "清理缓存",
        content: "确定要清理本地缓存吗？",
        success: (res) => {
          if (res.confirm) {
            common_vendor.index.clearStorageSync();
            common_vendor.index.showToast({ title: "清理成功", icon: "success" });
          }
        }
      });
    },
    showAbout() {
      common_vendor.index.showModal({
        title: "关于时光记",
        content: "时光记 - 记住每一个重要日子\n\n一款帮助您记住家人、朋友生日和纪念日的微信小程序。\n\n版本：1.0.0",
        showCancel: false
      });
    }
  }
};
function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
  return common_vendor.e({
    a: $data.userInfo
  }, $data.userInfo ? {
    b: $data.userInfo.avatar || "/static/default-avatar.png",
    c: common_vendor.t($data.userInfo.nickname || "微信用户"),
    d: common_vendor.t($options.getVipName($data.userInfo.vip_type))
  } : {}, {
    e: common_vendor.t($data.stats.record_count || 0),
    f: common_vendor.t($data.stats.record_limit || 8),
    g: common_vendor.t($data.stats.sms_count || 3),
    h: common_vendor.o((...args) => $options.goToSmsLogs && $options.goToSmsLogs(...args), "23"),
    i: common_vendor.o((...args) => $options.clearCache && $options.clearCache(...args), "f8"),
    j: common_vendor.o((...args) => $options.showAbout && $options.showAbout(...args), "da")
  });
}
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["render", _sfc_render], ["__scopeId", "data-v-b4180827"]]);
wx.createPage(MiniProgramPage);
