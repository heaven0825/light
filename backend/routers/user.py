"""
时光记 - 用户相关API (RESTful)
"""
import httpx
import os
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import User, Record
from schemas import UserResponse, UserUpdate, WxLoginRequest, ApiResponse
from utils.response import success, error

router = APIRouter(prefix="/api", tags=["用户"])


def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """获取当前用户（从 Authorization header 获取 openid）"""
    if not authorization:
        raise HTTPException(status_code=401, detail="缺少认证信息")
    
    # Authorization: Bearer <openid>
    if authorization.startswith("Bearer "):
        openid = authorization[7:]
    else:
        openid = authorization
    
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    
    return user


@router.post("/auth/login", response_model=ApiResponse)
async def wx_login(login_data: WxLoginRequest, db: Session = Depends(get_db)):
    """
    微信小程序登录
    POST /api/auth/login
    """
    appid = os.getenv("WECHAT_APPID")
    secret = os.getenv("WECHAT_SECRET")
    
    openid = None
    
    if appid and secret:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.weixin.qq.com/sns/jscode2session",
                    params={
                        "appid": appid,
                        "secret": secret,
                        "js_code": login_data.code,
                        "grant_type": "authorization_code"
                    }
                )
                data = response.json()
                if "openid" in data:
                    openid = data["openid"]
        except Exception as e:
            print(f"微信登录失败: {e}")
    
    if not openid:
        openid = login_data.code
    
    # 检查或创建用户
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        user = User(
            openid=openid,
            vip_type=0,
            sms_count=3
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return success({
        "openid": openid,
        "token": openid,  # 简化：直接用 openid 作为 token
        "user": {
            "id": user.id,
            "openid": user.openid,
            "nickname": user.nickname,
            "avatar": user.avatar,
            "vip_type": user.vip_type,
            "sms_count": user.sms_count
        }
    }, "登录成功")


@router.get("/user/me", response_model=ApiResponse)
def get_user_info(current_user: User = Depends(get_current_user)):
    """
    获取当前用户信息
    GET /api/user/me
    """
    return success({
        "id": current_user.id,
        "openid": current_user.openid,
        "nickname": current_user.nickname,
        "avatar": current_user.avatar,
        "vip_type": current_user.vip_type,
        "vip_expire_time": current_user.vip_expire_time,
        "sms_count": current_user.sms_count
    })


@router.put("/user/me", response_model=ApiResponse)
def update_user_info(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新用户信息
    PUT /api/user/me
    """
    if update_data.nickname is not None:
        current_user.nickname = update_data.nickname
    if update_data.avatar is not None:
        current_user.avatar = update_data.avatar
    
    db.commit()
    db.refresh(current_user)
    
    return success({
        "id": current_user.id,
        "openid": current_user.openid,
        "nickname": current_user.nickname,
        "avatar": current_user.avatar,
        "vip_type": current_user.vip_type,
        "sms_count": current_user.sms_count
    })


@router.get("/user/stats", response_model=ApiResponse)
def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户统计数据
    GET /api/user/stats
    """
    record_count = db.query(Record).filter(Record.openid == current_user.openid).count()
    limits = {0: 8, 1: 100, 2: 100}
    limit = limits.get(current_user.vip_type, 8)
    
    return success({
        "record_count": record_count,
        "record_limit": limit,
        "vip_type": current_user.vip_type,
        "sms_count": current_user.sms_count,
        "vip_expire_time": current_user.vip_expire_time
    })
