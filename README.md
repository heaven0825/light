# 时光记

记住每一个重要日子

## 项目简介

时光记是一款微信小程序，帮助用户记住家人、朋友、同事、客户的生日和纪念日。

### 核心功能

- 生日/纪念日记录，支持公历/农历
- 批量文本导入，自动识别日期
- 分组管理：家人/朋友/同事/客户
- 祝福语推荐，一键复制
- 微信服务通知 + 短信提醒
- 会员体系：免费/年卡(9.9元)/终身(39.9元)

## 项目结构

```
light/
├── backend/           # 后端 (FastAPI)
│   ├── main.py        # 主入口
│   ├── database.py     # 数据库配置
│   ├── models.py       # 数据模型
│   ├── schemas.py      # Pydantic schemas
│   ├── tasks.py        # 定时任务
│   ├── routers/        # API路由
│   │   ├── user.py     # 用户相关
│   │   ├── record.py   # 记录相关
│   │   ├── blessing.py # 祝福语
│   │   ├── order.py    # 订单相关
│   │   └── sms.py      # 短信相关
│   └── utils/
│       └── lunar.py    # 农历转换工具
├── front/             # 前端 (uni-app/Vue)
│   ├── src/
│   │   ├── App.vue     # 主组件
│   │   ├── api/        # API封装
│   │   ├── pages/      # 页面
│   │   └── styles/     # 样式
│   └── package.json
├── docs/              # 文档
│   ├── prd.md         # 产品需求文档
│   ├── 1.sql          # 数据库表结构
│   └── 上架文案.md     # 应用商店文案
└── README.md
```

## 后端部署

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并修改配置：

```bash
cp .env.example .env
```

### 3. 创建数据库

执行 `docs/1.sql` 创建数据库表。

### 4. 启动服务

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 前端部署

### 微信小程序

1. 安装 HBuilderX
2. 导入 `front` 目录
3. 修改 `manifest.json` 中的 appid
4. 运行到微信开发者工具

### Web 版本

```bash
cd front
npm install
npm run dev    # 开发模式
npm run build  # 生产构建
```

## 数据库表结构

| 表名 | 说明 |
|------|------|
| users | 用户表 |
| records | 生日/纪念日记录表 |
| blessings | 祝福语库表 |
| orders | 订单支付表 |
| sms_logs | 短信发送日志表 |

## API 接口

| 接口 | 说明 |
|------|------|
| POST /api/user/login | 微信登录 |
| GET /api/user/info | 获取用户信息 |
| GET /api/records/ | 获取记录列表 |
| POST /api/records/ | 创建记录 |
| POST /api/records/batch_import | 批量导入 |
| GET /api/blessings/ | 获取祝福语 |
| POST /api/order/create | 创建订单 |
| POST /api/sms/send | 发送短信 |

## 会员权益

| 权益 | 免费 | 年卡(9.9元) | 终身(39.9元) |
|------|------|-------------|--------------|
| 记录数 | 8条 | 100条 | 100条 |
| 祝福语 | 每组3条 | 无限 | 无限 |
| 短信 | 3条 | 无限 | 无限 |
| 自动年重复 | ❌ | ✅ | ✅ |

## License

MIT
