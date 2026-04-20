"use strict";
const common_vendor = require("../../common/vendor.js");
const api_index = require("../../api/index.js");
const _sfc_main = {
  data() {
    return {
      upcomingList: [],
      records: [],
      currentFilter: 0,
      currentDate: "",
      currentTime: "",
      currentLunar: "",
      timer: null,
      filterTabs: [
        { label: "全部", value: 0, icon: "📋" },
        { label: "家人", value: 1, icon: "👨‍👩‍👧" },
        { label: "朋友", value: 2, icon: "👫" },
        { label: "同事", value: 3, icon: "💼" },
        { label: "客户", value: 4, icon: "🤝" }
      ]
    };
  },
  computed: {
    filteredRecords() {
      if (this.currentFilter === 0)
        return this.records;
      return this.records.filter((r) => r.group_type === this.currentFilter);
    }
  },
  onLoad() {
    this.initLogin();
    this.loadDateInfo();
    this.updateTime();
    this.timer = setInterval(this.updateTime, 1e3);
  },
  onUnload() {
    if (this.timer)
      clearInterval(this.timer);
  },
  onShow() {
    this.loadData();
  },
  methods: {
    // 从后端加载日期信息（包含农历）
    async loadDateInfo() {
      try {
        const dateInfo = await api_index.dateApi.getNow();
        const lunar = dateInfo.lunar;
        this.currentLunar = `农历${lunar.month}${lunar.day}`;
      } catch (e) {
        console.error("获取日期信息失败:", e);
      }
    },
    // 更新阳历时间（每秒更新，分别显示日期和时间）
    updateTime() {
      const now = /* @__PURE__ */ new Date();
      const month = String(now.getMonth() + 1).padStart(2, "0");
      const day = String(now.getDate()).padStart(2, "0");
      const hours = String(now.getHours()).padStart(2, "0");
      const minutes = String(now.getMinutes()).padStart(2, "0");
      const seconds = String(now.getSeconds()).padStart(2, "0");
      this.currentDate = `${month}月${day}日`;
      this.currentTime = `${hours}:${minutes}:${seconds}`;
    },
    async initLogin() {
      let token = common_vendor.index.getStorageSync("token");
      if (!token) {
        try {
          const loginRes = await new Promise((resolve, reject) => {
            common_vendor.index.login({
              provider: "weixin",
              success: resolve,
              fail: reject
            });
          });
          if (loginRes.code) {
            const data = await api_index.authApi.login(loginRes.code);
            common_vendor.index.setStorageSync("token", data.token);
            common_vendor.index.setStorageSync("openid", data.openid);
            common_vendor.index.setStorageSync("user_info", data.user);
            console.log("登录成功 openid:", data.openid);
            this.loadData();
          }
        } catch (e) {
          console.error("登录失败:", e);
        }
      } else {
        this.loadData();
      }
    },
    async loadData() {
      try {
        const [upcoming, records] = await Promise.all([
          api_index.recordApi.getList({ days: 14 }),
          api_index.recordApi.getList()
        ]);
        this.upcomingList = upcoming || [];
        this.records = records || [];
      } catch (e) {
        console.error("加载失败", e);
      }
    },
    changeFilter(type) {
      this.currentFilter = type;
    },
    getGroupName(type) {
      const names = { 1: "家人", 2: "朋友", 3: "同事", 4: "客户" };
      return names[type] || "其他";
    },
    getGroupTagClass(type) {
      const classes = { 1: "tag-family", 2: "tag-friend", 3: "tag-colleague", 4: "tag-client" };
      return classes[type] || "";
    },
    getGroupDotClass(type) {
      const classes = { 1: "dot-family", 2: "dot-friend", 3: "dot-colleague", 4: "dot-client" };
      return classes[type] || "";
    },
    getGroupIcon(type) {
      const icons = { 0: "📋", 1: "👨‍👩‍👧", 2: "👫", 3: "💼", 4: "🤝" };
      return icons[type] || "📋";
    },
    getAvatarClass(type) {
      const classes = { 1: "avatar-family", 2: "avatar-friend", 3: "avatar-colleague", 4: "avatar-client" };
      return classes[type] || "";
    },
    calculateAge(year) {
      return (/* @__PURE__ */ new Date()).getFullYear() - year;
    },
    formatDate(item) {
      if (item.date_type === 2) {
        return item.lunar_month_text + item.lunar_day_text;
      } else {
        return item.month + "月" + item.day + "日";
      }
    },
    goToDetail(id) {
      common_vendor.index.navigateTo({ url: "/pages/detail/index?id=" + id });
    }
  }
};
function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
  return common_vendor.e({
    a: common_vendor.t($data.currentDate),
    b: common_vendor.t($data.currentTime),
    c: common_vendor.t($data.currentLunar),
    d: $data.upcomingList.length > 0
  }, $data.upcomingList.length > 0 ? {
    e: common_vendor.t($data.upcomingList.length)
  } : {}, {
    f: $data.upcomingList.length > 0
  }, $data.upcomingList.length > 0 ? {
    g: common_vendor.f($data.upcomingList.slice(0, 6), (item, k0, i0) => {
      return common_vendor.e({
        a: common_vendor.t(item.days_until),
        b: item.days_until === 0 ? 1 : "",
        c: common_vendor.t(item.name),
        d: item.date_type === 2
      }, item.date_type === 2 ? {} : {}, {
        e: common_vendor.t($options.formatDate(item)),
        f: item.age
      }, item.age ? {
        g: common_vendor.t(item.age)
      } : {}, {
        h: common_vendor.n($options.getGroupDotClass(item.group_type)),
        i: item.id,
        j: common_vendor.o(($event) => $options.goToDetail(item.id), item.id)
      });
    })
  } : {}, {
    h: common_vendor.t($data.records.length),
    i: common_vendor.f($data.filterTabs, (tab, k0, i0) => {
      return {
        a: common_vendor.t($options.getGroupIcon(tab.value)),
        b: common_vendor.t(tab.label),
        c: tab.value,
        d: common_vendor.n({
          active: $data.currentFilter === tab.value
        }),
        e: common_vendor.o(($event) => $options.changeFilter(tab.value), tab.value)
      };
    }),
    j: common_vendor.f($options.filteredRecords, (record, k0, i0) => {
      return common_vendor.e({
        a: common_vendor.t(record.name.charAt(0)),
        b: common_vendor.n($options.getAvatarClass(record.group_type)),
        c: common_vendor.t(record.name),
        d: common_vendor.t($options.getGroupName(record.group_type)),
        e: common_vendor.n($options.getGroupTagClass(record.group_type)),
        f: record.date_type === 2
      }, record.date_type === 2 ? {} : {}, {
        g: common_vendor.t($options.formatDate(record)),
        h: record.year
      }, record.year ? {
        i: common_vendor.t($options.calculateAge(record.year))
      } : {}, {
        j: record.id,
        k: common_vendor.o(($event) => $options.goToDetail(record.id), record.id)
      });
    }),
    k: $options.filteredRecords.length === 0
  }, $options.filteredRecords.length === 0 ? {} : {});
}
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["render", _sfc_render]]);
wx.createPage(MiniProgramPage);
