# 时光记 - 微信小程序前端

## 项目说明

时光记是一款帮助用户记住生日、纪念日的微信小程序。

## 技术栈

- uni-app (Vue 3)
- HBuilderX IDE
- 微信小程序

## 目录结构

```
front/
├── index.html          # 入口HTML
├── package.json        # 项目配置
├── vite.config.js      # Vite配置
└── src/
    ├── main.js         # 入口文件
    ├── App.vue         # 根组件
    ├── api/            # API接口封装
    ├── pages/          # 页面组件
    │   ├── detail/     # 记录详情/编辑
    │   ├── member/     # 会员中心
    │   ├── import/     # 批量导入
    │   ├── settings/   # 设置
    │   └── sms/        # 发送短信
    └── styles/         # 全局样式
```

## 使用 HBuilderX 开发

### 1. 下载 HBuilderX

访问 [HBuilderX 官网](https://www.dcloud.io/hbuilderx.html) 下载 IDE。

### 2. 导入项目

1. 打开 HBuilderX
2. 文件 → 导入 → 从本地目录导入
3. 选择 `front` 文件夹

### 3. 修改配置

修改 `src/static/pages.json` 中的 appid 为你的微信小程序 appid。

### 4. 运行项目

1. 点击右上角「运行」
2. 选择「运行到小程序模拟器」
3. 选择「微信开发者工具」

### 5. 编译发布

1. 点击「发行」
2. 选择「小程序-微信」
3. 输入小程序名称和 AppID

## 页面说明

### 首页 (App.vue)
- 展示即将到来的生日/纪念日
- 显示全部记录列表
- 支持分组筛选

### 添加/编辑记录 (pages/detail)
- 创建或编辑生日/纪念日记录
- 支持公历/农历切换
- 设置提醒方式

### 批量导入 (pages/import)
- 批量导入记录
- 支持多种日期格式识别

### 会员中心 (pages/member)
- 查看当前会员状态
- 购买年卡/终身会员

### 设置 (pages/settings)
- 用户信息
- 使用统计
- 短信记录

### 发送短信 (pages/sms)
- 选择祝福语
- 发送短信提醒
