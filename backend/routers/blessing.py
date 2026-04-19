"""
时光记 - 祝福语API
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models import Blessing, User
from schemas import BlessingResponse

router = APIRouter(prefix="/api/blessings", tags=["祝福语"])


@router.get("/", response_model=List[BlessingResponse])
def get_blessings(
    group_type: int = Query(..., ge=1, le=4, description="分组类型: 1=家人 2=朋友 3=同事 4=客户"),
    openid: str = Query(..., description="用户openid"),
    db: Session = Depends(get_db)
):
    """获取祝福语列表"""
    # 检查用户会员类型
    user = db.query(User).filter(User.openid == openid).first()
    
    query = db.query(Blessing).filter(
        Blessing.group_type == group_type,
        Blessing.status == 1
    )
    
    # 免费用户只返回前3条
    if user and user.vip_type == 0:
        blessings = query.order_by(Blessing.sort).limit(3).all()
    else:
        blessings = query.order_by(Blessing.sort).all()
    
    return blessings


@router.get("/all")
def get_all_blessings(
    openid: str = Query(...),
    db: Session = Depends(get_db)
):
    """获取所有分组的祝福语"""
    user = db.query(User).filter(User.openid == openid).first()
    
    blessings = db.query(Blessing).filter(Blessing.status == 1).order_by(
        Blessing.group_type, Blessing.sort
    ).all()
    
    # 按分组整理
    result = {1: [], 2: [], 3: [], 4: []}
    for b in blessings:
        # 免费用户每组限3条
        if user and user.vip_type == 0 and len(result[b.group_type]) >= 3:
            continue
        result[b.group_type].append({
            "id": b.id,
            "content": b.content
        })
    
    return result


# 管理员接口（生产环境需添加权限验证）
@router.post("/admin/add")
def add_blessing(
    group_type: int,
    content: str,
    sort: int = 0,
    db: Session = Depends(get_db)
):
    """添加祝福语（管理员接口）"""
    blessing = Blessing(
        group_type=group_type,
        content=content,
        sort=sort
    )
    db.add(blessing)
    db.commit()
    db.refresh(blessing)
    
    return {"id": blessing.id, "message": "添加成功"}
