"""
时光记 - 短信API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import os

from database import get_db
from models import User, Record, SmsLog
from schemas import SmsSendRequest, SmsLogResponse

router = APIRouter(prefix="/api/sms", tags=["短信"])


def send_sms(mobile: str, content: str) -> bool:
    """
    发送短信（实际需要对接短信服务商）
    这里使用模拟实现
    """
    # 实际环境对接短信API，如阿里云、腾讯云等
    # 这里简单模拟发送成功
    sms_api_key = os.getenv("SMS_API_KEY")
    if not sms_api_key:
        # 模拟模式
        print(f"[模拟发送短信] 手机号: {mobile}, 内容: {content}")
        return True
    
    # 实际短信发送逻辑
    # ...
    return True


@router.post("/send")
def send_sms_to_friend(
    openid: str,
    request: SmsSendRequest,
    db: Session = Depends(get_db)
):
    """发送短信给好友"""
    # 验证用户
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 检查短信条数
    if user.vip_type == 0 and user.sms_count <= 0:
        raise HTTPException(status_code=400, detail="免费短信已用完，请升级会员")
    
    # 验证记录
    record = db.query(Record).filter(
        Record.id == request.record_id,
        Record.openid == openid
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    # 发送短信
    success = send_sms(request.mobile, request.content)
    
    # 记录日志
    sms_log = SmsLog(
        openid=openid,
        record_id=request.record_id,
        mobile=request.mobile,
        content=request.content[:200],
        status=1 if success else 0
    )
    db.add(sms_log)
    
    # 扣减短信条数
    if user.vip_type == 0:
        user.sms_count -= 1
    
    db.commit()
    
    if success:
        return {"message": "发送成功", "remaining": user.sms_count if user.vip_type == 0 else "无限"}
    else:
        raise HTTPException(status_code=500, detail="发送失败")


@router.get("/logs")
def get_sms_logs(
    openid: str,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """获取短信发送记录"""
    logs = db.query(SmsLog).filter(
        SmsLog.openid == openid
    ).order_by(SmsLog.send_time.desc()).limit(limit).all()
    
    return [{
        "id": log.id,
        "record_id": log.record_id,
        "mobile": log.mobile,
        "content": log.content,
        "send_time": log.send_time,
        "status": log.status,
        "status_name": "成功" if log.status else "失败"
    } for log in logs]


@router.get("/remaining")
def get_sms_remaining(openid: str, db: Session = Depends(get_db)):
    """获取剩余短信条数"""
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return {
        "count": user.sms_count,
        "unlimited": user.vip_type > 0
    }
