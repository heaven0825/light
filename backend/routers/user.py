"""
时光记 - 用户相关API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import User, Record
from schemas import UserResponse, UserUpdate, UserInfo

router = APIRouter(prefix="/api/user", tags=["用户"])


@router.get("/info", response_model=UserResponse)
def get_user_info(openid: str, db: Session = Depends(get_db)):
    """获取用户信息"""
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


@router.post("/login", response_model=UserResponse)
def login(user_info: UserInfo, db: Session = Depends(get_db)):
    """
    微信登录/注册
    如果用户不存在则自动创建
    """
    user = db.query(User).filter(User.openid == user_info.openid).first()
    
    if not user:
        # 创建新用户
        user = User(
            openid=user_info.openid,
            nickname=user_info.nickname,
            avatar=user_info.avatar,
            vip_type=0,  # 免费用户
            sms_count=3  # 初始3条短信
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return user


@router.put("/update", response_model=UserResponse)
def update_user(openid: str, update_data: UserUpdate, db: Session = Depends(get_db)):
    """更新用户信息"""
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    if update_data.nickname is not None:
        user.nickname = update_data.nickname
    if update_data.avatar is not None:
        user.avatar = update_data.avatar
    
    db.commit()
    db.refresh(user)
    return user


@router.get("/stats")
def get_user_stats(openid: str, db: Session = Depends(get_db)):
    """获取用户统计数据"""
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    record_count = db.query(Record).filter(Record.openid == openid).count()
    
    # 根据会员类型确定记录上限
    record_limit = {0: 8, 1: 100, 2: 100}
    limit = record_limit.get(user.vip_type, 8)
    
    return {
        "record_count": record_count,
        "record_limit": limit,
        "vip_type": user.vip_type,
        "sms_count": user.sms_count if user.vip_type == 0 else "无限",
        "vip_expire_time": user.vip_expire_time if user.vip_type == 1 else None
    }
