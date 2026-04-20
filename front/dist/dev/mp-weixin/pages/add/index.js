"use strict";
const common_vendor = require("../../common/vendor.js");
const api_index = require("../../api/index.js");
const _sfc_main = {
  data() {
    return {
      mode: "batch",
      // 默认批量添加
      loading: false,
      // 批量导入
      importText: "",
      batchGroup: 1,
      placeholderText: "例如：\n0408 妈妈\n正月十五 爸爸\n1204 张三@朋友\n七月廿二 李四@同事",
      groupOptions: [
        { label: "家人", value: 1 },
        { label: "朋友", value: 2 },
        { label: "同事", value: 3 },
        { label: "客户", value: 4 }
      ],
      // 单条添加
      singleForm: {
        type: 1,
        name: "",
        group_type: 1,
        date_type: 1,
        month: null,
        day: null,
        year: ""
      },
      typeOptions: [
        { label: "生日", value: 1 },
        { label: "纪念日", value: 2 }
      ],
      dateTypeOptions: [
        { label: "公历", value: 1 },
        { label: "农历", value: 2 }
      ],
      monthRange: Array.from({ length: 12 }, (_, i) => i + 1 + "月"),
      dayRange: Array.from({ length: 31 }, (_, i) => i + 1 + "日")
    };
  },
  computed: {
    parsedItems() {
      const items = [];
      const lines = this.importText.split("\n").filter((l) => l.trim());
      const groupMap = {
        "家人": 1,
        "朋友": 2,
        "同事": 3,
        "客户": 4
      };
      for (const line of lines) {
        const parts = line.trim().split(/\s+/);
        if (parts.length < 2)
          continue;
        let dateStr = parts[0];
        let name = parts.slice(1).join(" ");
        let groupType = this.batchGroup;
        if (name.includes("@")) {
          const [realName, groupStr] = name.split("@");
          name = realName;
          groupType = groupMap[groupStr] || this.batchGroup;
        }
        if (dateStr.includes("月") || dateStr.includes("初") || dateStr.includes("廿")) {
          const lunarMap = {
            "正": 1,
            "一": 1,
            "二": 2,
            "三": 3,
            "四": 4,
            "五": 5,
            "六": 6,
            "七": 7,
            "八": 8,
            "九": 9,
            "十": 10,
            "冬": 11,
            "腊": 12
          };
          const dayMap = {
            "初一": 1,
            "初二": 2,
            "初三": 3,
            "初四": 4,
            "初五": 5,
            "初六": 6,
            "初七": 7,
            "初八": 8,
            "初九": 9,
            "初十": 10,
            "十一": 11,
            "十二": 12,
            "十三": 13,
            "十四": 14,
            "十五": 15,
            "十六": 16,
            "十七": 17,
            "十八": 18,
            "十九": 19,
            "二十": 20,
            "廿一": 21,
            "廿二": 22,
            "廿三": 23,
            "廿四": 24,
            "廿五": 25,
            "廿六": 26,
            "廿七": 27,
            "廿八": 28,
            "廿九": 29,
            "三十": 30
          };
          let month = 1, day = 1;
          for (const [k, v] of Object.entries(lunarMap)) {
            if (dateStr.startsWith(k) || dateStr.startsWith(k + "月")) {
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
            name,
            group_type: groupType,
            lunar: true,
            displayDate: `${month}/${day}`
          });
        } else if (/^\d{4}$/.test(dateStr)) {
          const month = parseInt(dateStr.slice(0, 2));
          const day = parseInt(dateStr.slice(2));
          items.push({
            date: dateStr,
            name,
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
    goBack() {
      common_vendor.index.navigateBack();
    },
    getGroupLabel(type) {
      const names = { 1: "家人", 2: "朋友", 3: "同事", 4: "客户" };
      return names[type] || "其他";
    },
    // 批量导入方法
    changeBatchGroup(e) {
      this.batchGroup = this.groupOptions[e.detail.value].value;
    },
    async startImport() {
      if (this.parsedItems.length === 0) {
        return common_vendor.index.showToast({ title: "请输入导入内容", icon: "none" });
      }
      this.loading = true;
      try {
        const items = this.parsedItems.map((item) => ({
          date: item.date,
          name: item.name,
          type: 1,
          lunar: item.lunar
        }));
        const result = await api_index.recordApi.batchImport(items, this.batchGroup);
        common_vendor.index.showModal({
          title: "导入完成",
          content: `成功导入 ${result.imported} 条${result.failed > 0 ? `，失败 ${result.failed} 条` : ""}`,
          showCancel: false,
          success: () => {
            common_vendor.index.navigateBack();
          }
        });
      } catch (e) {
        common_vendor.index.showToast({ title: e.detail || "导入失败", icon: "none" });
      } finally {
        this.loading = false;
      }
    },
    // 单条添加方法
    changeType(e) {
      this.singleForm.type = parseInt(e.detail.value) + 1;
    },
    changeSingleGroup(e) {
      this.singleForm.group_type = this.groupOptions[e.detail.value].value;
    },
    changeDateType(e) {
      this.singleForm.date_type = parseInt(e.detail.value) + 1;
    },
    async saveSingle() {
      if (!this.singleForm.name.trim()) {
        return common_vendor.index.showToast({ title: "请输入姓名", icon: "none" });
      }
      if (!this.singleForm.month || !this.singleForm.day) {
        return common_vendor.index.showToast({ title: "请选择日期", icon: "none" });
      }
      this.loading = true;
      try {
        const yearVal = this.singleForm.year && this.singleForm.year !== "" ? parseInt(this.singleForm.year) : null;
        await api_index.recordApi.create({
          type: this.singleForm.type,
          name: this.singleForm.name,
          group_type: this.singleForm.group_type,
          date_type: this.singleForm.date_type,
          month: parseInt(this.singleForm.month),
          day: parseInt(this.singleForm.day),
          year: yearVal,
          remind_type: "1,7",
          sms_remind: 0
        });
        common_vendor.index.showToast({ title: "添加成功", icon: "success" });
        setTimeout(() => common_vendor.index.navigateBack(), 1500);
      } catch (e) {
        common_vendor.index.showToast({ title: e.detail || "保存失败", icon: "none" });
      } finally {
        this.loading = false;
      }
    }
  }
};
function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
  return common_vendor.e({
    a: common_vendor.n({
      active: $data.mode === "batch"
    }),
    b: common_vendor.o(($event) => $data.mode = "batch", "22"),
    c: common_vendor.n({
      active: $data.mode === "single"
    }),
    d: common_vendor.o(($event) => $data.mode = "single", "45"),
    e: $data.mode === "batch"
  }, $data.mode === "batch" ? common_vendor.e({
    f: common_vendor.t($options.getGroupLabel($data.batchGroup)),
    g: $data.groupOptions,
    h: common_vendor.o((...args) => $options.changeBatchGroup && $options.changeBatchGroup(...args), "4a"),
    i: $data.placeholderText,
    j: $data.importText,
    k: common_vendor.o(($event) => $data.importText = $event.detail.value, "f7"),
    l: $options.parsedItems.length > 0
  }, $options.parsedItems.length > 0 ? {
    m: common_vendor.t($options.parsedItems.length),
    n: common_vendor.f($options.parsedItems, (item, index, i0) => {
      return common_vendor.e({
        a: item.lunar
      }, item.lunar ? {} : {}, {
        b: common_vendor.t(item.displayDate),
        c: common_vendor.t(item.name),
        d: common_vendor.t($options.getGroupLabel(item.group_type)),
        e: index
      });
    })
  } : {}, {
    o: common_vendor.t($data.loading ? "导入中..." : "开始导入"),
    p: common_vendor.o((...args) => $options.startImport && $options.startImport(...args), "0e"),
    q: $data.loading || $options.parsedItems.length === 0
  }) : {}, {
    r: $data.mode === "single"
  }, $data.mode === "single" ? common_vendor.e({
    s: common_vendor.t($data.typeOptions[$data.singleForm.type - 1].label),
    t: $data.typeOptions,
    v: common_vendor.o((...args) => $options.changeType && $options.changeType(...args), "5d"),
    w: common_vendor.t($data.singleForm.type === 1 ? "姓名" : "标题"),
    x: $data.singleForm.type === 1 ? "请输入姓名" : "请输入标题",
    y: $data.singleForm.name,
    z: common_vendor.o(($event) => $data.singleForm.name = $event.detail.value, "1f"),
    A: common_vendor.t($options.getGroupLabel($data.singleForm.group_type)),
    B: $data.groupOptions,
    C: common_vendor.o((...args) => $options.changeSingleGroup && $options.changeSingleGroup(...args), "71"),
    D: common_vendor.t($data.dateTypeOptions[$data.singleForm.date_type - 1].label),
    E: $data.dateTypeOptions,
    F: common_vendor.o((...args) => $options.changeDateType && $options.changeDateType(...args), "ca"),
    G: common_vendor.t($data.singleForm.month || "选择"),
    H: $data.monthRange,
    I: common_vendor.o((e) => $data.singleForm.month = parseInt(e.detail.value) + 1, "9c"),
    J: common_vendor.t($data.singleForm.day || "选择"),
    K: $data.dayRange,
    L: common_vendor.o((e) => $data.singleForm.day = parseInt(e.detail.value) + 1, "19"),
    M: $data.singleForm.type === 1
  }, $data.singleForm.type === 1 ? {
    N: $data.singleForm.year,
    O: common_vendor.o(($event) => $data.singleForm.year = $event.detail.value, "39")
  } : {}, {
    P: common_vendor.t($data.loading ? "保存中..." : "保存"),
    Q: common_vendor.o((...args) => $options.saveSingle && $options.saveSingle(...args), "a7"),
    R: $data.loading
  }) : {});
}
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["render", _sfc_render], ["__scopeId", "data-v-602d3812"]]);
wx.createPage(MiniProgramPage);
