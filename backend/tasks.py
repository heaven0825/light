"""
时光记 - 定时任务
检查生日/纪念日提醒
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import User, Record, SmsLog
from utils.lunar import get_next_lunar_birthday


def check_reminders(db: Session):
    """
    检查需要提醒的记录
    建议每天早上8点执行
    """
    now = datetime.now()
    today = now.date()
    
    # 获取所有开启提醒的记录
    records = db.query(Record).filter(
        Record.remind_type.isnot(None)
    ).all()
    
    for record in records:
        # 计算下一个生日/纪念日的日期
        if record.date_type == 2:  # 农历
            next_date = get_next_lunar_birthday(record.month, record.day, now)
        else:  # 公历
            try:
                next_date = datetime(now.year, record.month, min(record.day, 28))
                if next_date <= now:
                    next_date = datetime(now.year + 1, record.month, min(record.day, 28))
            except:
                continue
        
        # 计算距离天数
        days_until = (next_date.date() - today).days
        
        # 检查是否需要提醒
        if record.remind_type:
            remind_days = [int(d) for d in record.remind_type.split(',') if d.strip().isdigit()]
            
            if days_until in remind_days:
                user = db.query(User).filter(User.openid == record.openid).first()
                if user:
                    # 记录待发送的提醒（实际发送由微信服务通知/短信服务处理）
                    print(f"[提醒] {user.openid}: {record.name} - {days_until}天后 ({next_date.strftime('%Y-%m-%d')})")
                    
                    # 如果开启短信提醒且是付费用户，发送短信
                    if record.sms_remind == 1 and user.vip_type > 0:
                        # 这里调用实际的短信发送逻辑
                        print(f"[短信提醒] {record.name} ({user.sms_count}条剩余)")


def check_vip_expire(db: Session):
    """
    检查年卡会员是否到期
    每天执行一次
    """
    now = datetime.now()
    
    # 查找即将到期的年卡用户（7天内）
    expire_date = now + timedelta(days=7)
    
    expiring_users = db.query(User).filter(
        User.vip_type == 1,
        User.vip_expire_time <= expire_date,
        User.vip_expire_time > now
    ).all()
    
    for user in expiring_users:
        days_left = (user.vip_expire_time - now).days
        print(f"[年卡到期提醒] {user.openid}: 会员将在{days_left}天后到期")


def yearly_repeat_check(db: Session):
    """
    检查是否需要为付费用户创建明年的提醒记录
    每年1月1日执行
    """
    now = datetime.now()
    
    # 获取所有付费用户
    vip_users = db.query(User).filter(User.vip_type.in_([1, 2])).all()
    
    for user in vip_users:
        # 获取该用户今年的生日/纪念日记录
        records = db.query(Record).filter(
            Record.openid == user.openid,
            Record.type == 1  # 生日
        ).all()
        
        # 对于付费用户，确保记录设置了自动年重复
        for record in records:
            # 这里可以添加逻辑来自动更新或创建新记录
            # 实际实现可能需要根据业务逻辑调整
            pass
    
    print(f"[年度检查] 已处理 {len(vip_users)} 位付费用户")
