"use strict";
const common_vendor = require("../../common/vendor.js");
const api_index = require("../../api/index.js");
const _sfc_main = {
  data() {
    return {
      recordId: null,
      recordName: "",
      mobile: "",
      blessings: [],
      selectedBlessing: "",
      smsContent: "",
      remaining: null,
      loading: false
    };
  },
  onLoad(options) {
    this.recordId = options.id;
    this.recordName = decodeURIComponent(options.name || "");
    this.loadData();
  },
  methods: {
    async loadData() {
      try {
        const blessings = await api_index.blessingApi.getList(1);
        this.blessings = blessings;
        const remaining = await api_index.smsApi.getRemaining();
        this.remaining = remaining.unlimited ? "无限" : remaining.count;
      } catch (e) {
        console.error(e);
      }
    },
    selectBlessing(content) {
      this.selectedBlessing = content;
      this.smsContent = `【时光记】亲爱的朋友，${content} 祝一切顺利！`;
    },
    async sendSms() {
      if (!this.mobile || this.mobile.length !== 11) {
        return common_vendor.index.showToast({ title: "请输入正确的手机号", icon: "none" });
      }
      if (!this.smsContent) {
        return common_vendor.index.showToast({ title: "请选择祝福语", icon: "none" });
      }
      this.loading = true;
      try {
        const result = await api_index.smsApi.send({
          record_id: this.recordId,
          mobile: this.mobile,
          content: this.smsContent
        });
        common_vendor.index.showToast({ title: "发送成功", icon: "success" });
        this.remaining = result.remaining;
        setTimeout(() => common_vendor.index.navigateBack(), 1500);
      } catch (e) {
        common_vendor.index.showToast({ title: e.detail || "发送失败", icon: "none" });
      } finally {
        this.loading = false;
      }
    }
  }
};
function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
  return common_vendor.e({
    a: common_vendor.t($data.recordName),
    b: $data.mobile,
    c: common_vendor.o(($event) => $data.mobile = $event.detail.value, "bf"),
    d: common_vendor.f($data.blessings, (item, k0, i0) => {
      return {
        a: common_vendor.t(item.content),
        b: item.id,
        c: common_vendor.n({
          active: $data.selectedBlessing === item.content
        }),
        d: common_vendor.o(($event) => $options.selectBlessing(item.content), item.id)
      };
    }),
    e: common_vendor.t($data.smsContent || "请选择或编辑祝福语"),
    f: common_vendor.t($data.loading ? "发送中..." : "发送短信"),
    g: common_vendor.o((...args) => $options.sendSms && $options.sendSms(...args), "4f"),
    h: $data.loading || !$data.mobile,
    i: $data.remaining !== null
  }, $data.remaining !== null ? {
    j: common_vendor.t($data.remaining === "无限" ? "无限" : $data.remaining + "条")
  } : {});
}
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["render", _sfc_render], ["__scopeId", "data-v-d15c5171"]]);
wx.createPage(MiniProgramPage);
