"""
时光记 - 祝福语API (RESTful)
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models import Blessing
from schemas import BlessingResponse, ApiResponse
from routers.user import get_current_user
from utils.response import success

router = APIRouter(prefix="/api/blessings", tags=["祝福语"])


@router.get("/", response_model=ApiResponse)
def get_blessings(
    group_type: Optional[int] = Query(default=None, description="分组类型"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取祝福语列表
    GET /api/blessings
    GET /api/blessings?group_type=1
    """
    query = db.query(Blessing)
    
    if group_type:
        query = query.filter(Blessing.group_type == group_type)
    
    blessings = query.limit(20).all()
    
    return success([
        {
            "id": b.id,
            "group_type": b.group_type,
            "content": b.content
        }
        for b in blessings
    ])


@router.get("/all", response_model=ApiResponse)
def get_all_blessings(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取所有祝福语（按分组）
    GET /api/blessings/all
    """
    blessings = db.query(Blessing).all()
    
    result = {}
    for b in blessings:
        if b.group_type not in result:
            result[b.group_type] = []
        result[b.group_type].append({
            "id": b.id,
            "content": b.content
        })
    
    return success(result)
