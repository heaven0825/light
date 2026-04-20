"""
时光记 - 短信API (RESTful)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import SmsLog, User, Record
from schemas import SmsSendRequest, ApiResponse
from routers.user import get_current_user
from utils.response import success

router = APIRouter(prefix="/api/sms", tags=["短信"])


@router.post("/send", response_model=ApiResponse)
def send_sms(
    sms_data: SmsSendRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    发送短信
    POST /api/sms/send
    """
    # 检查用户短信条数
    if current_user.vip_type == 0 and current_user.sms_count <= 0:
        raise HTTPException(status_code=400, detail="短信条数已用完，请升级会员")
    
    # 检查记录是否存在
    record = db.query(Record).filter(
        Record.id == sms_data.record_id,
        Record.openid == current_user.openid
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    # 记录短信日志
    sms_log = SmsLog(
        openid=current_user.openid,
        record_id=sms_data.record_id,
        mobile=sms_data.mobile,
        content=sms_data.content,
        status=1  # 发送成功（简化处理）
    )
    db.add(sms_log)
    
    # 扣减短信条数
    if current_user.vip_type == 0:
        current_user.sms_count -= 1
    
    db.commit()
    
    return success({
        "log_id": sms_log.id,
        "status": 1
    }, "发送成功")


@router.get("/logs", response_model=ApiResponse)
def get_sms_logs(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取短信发送记录
    GET /api/sms/logs?limit=20
    """
    logs = db.query(SmsLog).filter(
        SmsLog.openid == current_user.openid
    ).order_by(SmsLog.send_time.desc()).limit(limit).all()
    
    return success([
        {
            "id": log.id,
            "record_id": log.record_id,
            "mobile": log.mobile,
            "content": log.content,
            "status": log.status,
            "send_time": log.send_time.isoformat() if log.send_time else None
        }
        for log in logs
    ])


@router.get("/remaining", response_model=ApiResponse)
def get_remaining_sms(
    current_user: User = Depends(get_current_user)
):
    """
    获取剩余短信条数
    GET /api/sms/remaining
    """
    if current_user.vip_type > 0:
        return success({
            "count": -1,  # 无限
            "unlimited": True
        })
    
    return success({
        "count": current_user.sms_count,
        "unlimited": False
    })
