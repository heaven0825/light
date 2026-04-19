/*
  时光记小程序 - 完整数据库表结构（带详细注释）
  适用于 MySQL 5.7 / 8.0
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- 1. 用户表
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `openid` varchar(50) NOT NULL COMMENT '微信唯一标识openid',
  `nickname` varchar(50) DEFAULT NULL COMMENT '微信昵称',
  `avatar` varchar(255) DEFAULT NULL COMMENT '微信头像',
  `vip_type` tinyint NOT NULL DEFAULT '0' COMMENT '会员类型 0=免费 1=年卡 2=终身',
  `vip_expire_time` datetime DEFAULT NULL COMMENT '年卡到期时间',
  `sms_count` int NOT NULL DEFAULT '3' COMMENT '免费短信条数，默认3条',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `openid` (`openid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- ----------------------------
-- 2. 生日/纪念日记录表
-- ----------------------------
DROP TABLE IF EXISTS `records`;
CREATE TABLE `records` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `openid` varchar(50) NOT NULL COMMENT '所属用户openid',
  `type` tinyint NOT NULL DEFAULT '1' COMMENT '记录类型 1=生日 2=纪念日',
  `name` varchar(30) NOT NULL COMMENT '姓名/标题',
  `group_type` tinyint NOT NULL DEFAULT '1' COMMENT '分组 1=家人 2=朋友 3=同事 4=客户',
  `date_type` tinyint NOT NULL DEFAULT '1' COMMENT '日期类型 1=公历 2=农历',
  `month` tinyint NOT NULL COMMENT '月份 1-12',
  `day` tinyint NOT NULL COMMENT '日期 1-30',
  `year` int DEFAULT NULL COMMENT '出生年份（可选，用于计算年龄）',
  `remind_type` varchar(50) DEFAULT NULL COMMENT '提醒配置 1,3,7代表提前1、3、7天',
  `sms_remind` tinyint DEFAULT '0' COMMENT '是否开启短信提醒 0=关闭 1=开启',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `openid` (`openid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='生日/纪念日记录表';

-- ----------------------------
-- 3. 祝福语库表
-- ----------------------------
DROP TABLE IF EXISTS `blessings`;
CREATE TABLE `blessings` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `group_type` tinyint NOT NULL COMMENT '适用分组 1=家人 2=朋友 3=同事 4=客户',
  `content` text NOT NULL COMMENT '祝福语内容',
  `sort` int DEFAULT '0' COMMENT '排序号，越小越靠前',
  `status` tinyint DEFAULT '1' COMMENT '状态 1=启用 0=禁用',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='祝福语库表';

-- ----------------------------
-- 4. 订单表（会员支付）
-- ----------------------------
DROP TABLE IF EXISTS `orders`;
CREATE TABLE `orders` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `order_no` varchar(32) NOT NULL COMMENT '订单号（唯一）',
  `openid` varchar(50) NOT NULL COMMENT '下单用户openid',
  `pay_type` tinyint NOT NULL COMMENT '支付类型 1=年卡 2=终身会员',
  `amount` decimal(10,2) NOT NULL COMMENT '支付金额',
  `pay_status` tinyint DEFAULT '0' COMMENT '支付状态 0=未支付 1=已支付',
  `pay_time` datetime DEFAULT NULL COMMENT '支付时间',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `order_no` (`order_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单支付表';

-- ----------------------------
-- 5. 短信发送日志表
-- ----------------------------
DROP TABLE IF EXISTS `sms_logs`;
CREATE TABLE `sms_logs` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `openid` varchar(50) NOT NULL COMMENT '发送用户openid',
  `record_id` int NOT NULL COMMENT '关联的记录ID',
  `mobile` varchar(11) NOT NULL COMMENT '接收短信的手机号',
  `content` varchar(255) NOT NULL COMMENT '短信内容',
  `send_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '发送时间',
  `status` tinyint DEFAULT '1' COMMENT '发送状态 1=成功 0=失败',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='短信发送日志表';

SET FOREIGN_KEY_CHECKS = 1;