"""
时光记 - 数据库模型定义
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Numeric, SmallInteger
from sqlalchemy.sql import func
from database import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    openid = Column(String(50), unique=True, nullable=False, index=True)
    nickname = Column(String(50), nullable=True)
    avatar = Column(String(255), nullable=True)
    vip_type = Column(SmallInteger, default=0)  # 0=免费 1=年卡 2=终身
    vip_expire_time = Column(DateTime, nullable=True)
    sms_count = Column(Integer, default=3)  # 免费短信条数
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Record(Base):
    """生日/纪念日记录表"""
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    openid = Column(String(50), nullable=False, index=True)
    type = Column(SmallInteger, default=1)  # 1=生日 2=纪念日
    name = Column(String(30), nullable=False)
    group_type = Column(SmallInteger, default=1)  # 1=家人 2=朋友 3=同事 4=客户
    date_type = Column(SmallInteger, default=1)  # 1=公历 2=农历
    month = Column(Integer, nullable=False)  # 1-12
    day = Column(Integer, nullable=False)  # 1-30
    year = Column(Integer, nullable=True)  # 出生年份
    remind_type = Column(String(50), nullable=True)  # 1,3,7 提前天数
    sms_remind = Column(SmallInteger, default=0)  # 0=关闭 1=开启
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Blessing(Base):
    """祝福语库表"""
    __tablename__ = "blessings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_type = Column(SmallInteger, nullable=False)  # 1=家人 2=朋友 3=同事 4=客户
    content = Column(Text, nullable=False)
    sort = Column(Integer, default=0)
    status = Column(SmallInteger, default=1)  # 1=启用 0=禁用


class Order(Base):
    """订单支付表"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_no = Column(String(32), unique=True, nullable=False)
    openid = Column(String(50), nullable=False)
    pay_type = Column(SmallInteger, nullable=False)  # 1=年卡 2=终身会员
    amount = Column(Numeric(10, 2), nullable=False)
    pay_status = Column(SmallInteger, default=0)  # 0=未支付 1=已支付
    pay_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class SmsLog(Base):
    """短信发送日志表"""
    __tablename__ = "sms_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    openid = Column(String(50), nullable=False)
    record_id = Column(Integer, nullable=False)
    mobile = Column(String(11), nullable=False)
    content = Column(String(255), nullable=False)
    send_time = Column(DateTime, server_default=func.now())
    status = Column(SmallInteger, default=1)  # 1=成功 0=失败
