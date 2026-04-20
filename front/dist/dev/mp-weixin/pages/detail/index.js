"use strict";
const common_vendor = require("../../common/vendor.js");
const api_index = require("../../api/index.js");
const _sfc_main = {
  data() {
    return {
      form: {
        id: null,
        type: 1,
        name: "",
        group_type: 1,
        date_type: 1,
        month: "",
        day: "",
        year: "",
        remind_type: "1,7",
        sms_remind: 0
      },
      typeOptions: [
        { label: "生日", value: 1 },
        { label: "纪念日", value: 2 }
      ],
      groupOptions: [
        { label: "家人", value: 1 },
        { label: "朋友", value: 2 },
        { label: "同事", value: 3 },
        { label: "客户", value: 4 }
      ],
      dateTypeOptions: [
        { label: "公历", value: 1 },
        { label: "农历", value: 2 }
      ],
      remindOptions: [
        { label: "1天", value: "1", icon: "📱" },
        { label: "3天", value: "3", icon: "📅" },
        { label: "7天", value: "7", icon: "📆" },
        { label: "14天", value: "14", icon: "🗓️" }
      ],
      selectedReminds: ["1", "7"],
      loading: false,
      monthRange: Array.from({ length: 12 }, (_, i) => i + 1 + "月"),
      dayRange: Array.from({ length: 31 }, (_, i) => i + 1 + "日")
    };
  },
  onLoad(options) {
    if (options.id) {
      this.form.id = parseInt(options.id);
      this.loadRecord();
    }
  },
  methods: {
    goBack() {
      common_vendor.index.navigateBack();
    },
    async loadRecord() {
      try {
        const record = await api_index.recordApi.getOne(this.form.id);
        this.form = {
          id: record.id,
          type: record.type,
          name: record.name,
          group_type: record.group_type,
          date_type: record.date_type,
          month: record.month,
          day: record.day,
          year: record.year || "",
          remind_type: record.remind_type || "1,7",
          sms_remind: record.sms_remind || 0
        };
        if (record.remind_type) {
          this.selectedReminds = record.remind_type.split(",");
        }
      } catch (e) {
        common_vendor.index.showToast({ title: "加载失败", icon: "none" });
      }
    },
    changeType(e) {
      this.form.type = parseInt(e.detail.value) + 1;
    },
    changeGroup(e) {
      this.form.group_type = parseInt(e.detail.value) + 1;
    },
    changeDateType(e) {
      this.form.date_type = parseInt(e.detail.value) + 1;
    },
    getGroupLabel(type) {
      const names = { 1: "家人", 2: "朋友", 3: "同事", 4: "客户" };
      return names[type] || "其他";
    },
    toggleRemind(value) {
      const index = this.selectedReminds.indexOf(value);
      if (index > -1) {
        this.selectedReminds.splice(index, 1);
      } else {
        this.selectedReminds.push(value);
      }
      this.form.remind_type = this.selectedReminds.join(",");
    },
    toggleSms() {
      this.form.sms_remind = this.form.sms_remind ? 0 : 1;
    },
    async save() {
      if (!this.form.name.trim()) {
        return common_vendor.index.showToast({ title: "请输入姓名", icon: "none" });
      }
      if (!this.form.month || !this.form.day) {
        return common_vendor.index.showToast({ title: "请选择日期", icon: "none" });
      }
      this.loading = true;
      try {
        const yearVal = this.form.year && this.form.year !== "" ? parseInt(this.form.year) : null;
        if (this.form.id) {
          await api_index.recordApi.update(this.form.id, {
            type: this.form.type,
            name: this.form.name,
            group_type: this.form.group_type,
            date_type: this.form.date_type,
            month: parseInt(this.form.month),
            day: parseInt(this.form.day),
            year: yearVal,
            remind_type: this.form.remind_type,
            sms_remind: this.form.sms_remind
          });
          common_vendor.index.showToast({ title: "更新成功", icon: "success" });
        } else {
          await api_index.recordApi.create({
            type: this.form.type,
            name: this.form.name,
            group_type: this.form.group_type,
            date_type: this.form.date_type,
            month: parseInt(this.form.month),
            day: parseInt(this.form.day),
            year: yearVal,
            remind_type: this.form.remind_type,
            sms_remind: this.form.sms_remind
          });
          common_vendor.index.showToast({ title: "添加成功", icon: "success" });
        }
        setTimeout(() => common_vendor.index.navigateBack(), 1500);
      } catch (e) {
        common_vendor.index.showToast({ title: e.detail || "保存失败", icon: "none" });
      } finally {
        this.loading = false;
      }
    },
    async deleteRecord() {
      if (!this.form.id)
        return;
      common_vendor.index.showModal({
        title: "确认删除",
        content: "确定要删除这条记录吗？",
        success: async (res) => {
          if (res.confirm) {
            try {
              await api_index.recordApi.delete(this.form.id);
              common_vendor.index.showToast({ title: "已删除", icon: "success" });
              setTimeout(() => common_vendor.index.navigateBack(), 1500);
            } catch (e) {
              common_vendor.index.showToast({ title: "删除失败", icon: "none" });
            }
          }
        }
      });
    }
  }
};
function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
  return common_vendor.e({
    a: common_vendor.t($data.typeOptions[$data.form.type - 1].label),
    b: $data.typeOptions,
    c: common_vendor.o((...args) => $options.changeType && $options.changeType(...args), "6e"),
    d: common_vendor.t($data.form.type === 1 ? "姓名" : "标题"),
    e: $data.form.type === 1 ? "请输入姓名" : "请输入标题",
    f: $data.form.name,
    g: common_vendor.o(($event) => $data.form.name = $event.detail.value, "b0"),
    h: common_vendor.t($options.getGroupLabel($data.form.group_type)),
    i: $data.groupOptions,
    j: common_vendor.o((...args) => $options.changeGroup && $options.changeGroup(...args), "66"),
    k: common_vendor.t($data.dateTypeOptions[$data.form.date_type - 1].label),
    l: $data.dateTypeOptions,
    m: common_vendor.o((...args) => $options.changeDateType && $options.changeDateType(...args), "4b"),
    n: common_vendor.t($data.form.month || "选择"),
    o: $data.monthRange,
    p: common_vendor.o((e) => $data.form.month = parseInt(e.detail.value) + 1, "fa"),
    q: common_vendor.t($data.form.day || "选择"),
    r: $data.dayRange,
    s: common_vendor.o((e) => $data.form.day = parseInt(e.detail.value) + 1, "92"),
    t: $data.form.type === 1
  }, $data.form.type === 1 ? {
    v: $data.form.year,
    w: common_vendor.o(($event) => $data.form.year = $event.detail.value, "b1")
  } : {}, {
    x: common_vendor.f($data.remindOptions, (opt, k0, i0) => {
      return {
        a: common_vendor.t(opt.icon),
        b: common_vendor.t(opt.label),
        c: opt.value,
        d: common_vendor.n({
          active: $data.selectedReminds.includes(opt.value)
        }),
        e: common_vendor.o(($event) => $options.toggleRemind(opt.value), opt.value)
      };
    }),
    y: $data.form.sms_remind === 1,
    z: common_vendor.o((...args) => $options.toggleSms && $options.toggleSms(...args), "d4"),
    A: common_vendor.t($data.loading ? "保存中..." : "保存"),
    B: common_vendor.o((...args) => $options.save && $options.save(...args), "d8"),
    C: $data.loading,
    D: $data.form.id
  }, $data.form.id ? {
    E: common_vendor.o((...args) => $options.deleteRecord && $options.deleteRecord(...args), "a5")
  } : {});
}
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["render", _sfc_render], ["__scopeId", "data-v-02b149d6"]]);
wx.createPage(MiniProgramPage);
