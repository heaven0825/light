"""
时光记 - 生日/纪念日记录API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
from models import Record, User
from schemas import RecordCreate, RecordUpdate, RecordResponse
from utils.lunar import parse_lunar_date, parse_solar_date, calculate_age

router = APIRouter(prefix="/api/records", tags=["记录"])


def check_record_limit(openid: str, db: Session) -> tuple:
    """检查记录数量限制"""
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    record_count = db.query(Record).filter(Record.openid == openid).count()
    
    # 根据会员类型确定记录上限
    limits = {0: 8, 1: 100, 2: 100}
    limit = limits.get(user.vip_type, 8)
    
    return record_count, limit


@router.get("/", response_model=List[RecordResponse])
def get_records(
    openid: str,
    group_type: Optional[int] = None,
    type: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """获取用户的所有记录"""
    query = db.query(Record).filter(Record.openid == openid)
    
    if group_type:
        query = query.filter(Record.group_type == group_type)
    if type:
        query = query.filter(Record.type == type)
    
    records = query.order_by(Record.month, Record.day).all()
    return records


@router.get("/upcoming")
def get_upcoming_records(
    openid: str,
    days: int = Query(default=7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """获取即将到来的生日/纪念日"""
    records = db.query(Record).filter(Record.openid == openid).all()
    now = datetime.now()
    
    upcoming = []
    for record in records:
        # 计算距离下一个日期的天数
        current_month = now.month
        current_day = now.day
        
        # 简单计算：如果还没过，今年有这么多天
        if record.month > current_month or (record.month == current_month and record.day >= current_day):
            days_until = (datetime(now.year, record.month, min(record.day, 28)) - now).days
        else:
            # 已经过了，计算到明年的天数
            next_year = now.year + 1
            days_until = (datetime(next_year, record.month, min(record.day, 28)) - now).days
        
        if 0 <= days_until <= days:
            # 计算年龄（如果提供年份且是生日类型）
            age = None
            if record.year and record.type == 1:
                age = now.year - record.year
                if (record.month, record.day) > (now.month, now.day):
                    age -= 1
            
            upcoming.append({
                "id": record.id,
                "name": record.name,
                "type": record.type,
                "month": record.month,
                "day": record.day,
                "group_type": record.group_type,
                "date_type": record.date_type,
                "days_until": days_until,
                "age": age,
                "lunar_display": "农历" if record.date_type == 2 else ""
            })
    
    # 按天数排序
    upcoming.sort(key=lambda x: x["days_until"])
    return upcoming


@router.get("/{record_id}", response_model=RecordResponse)
def get_record(record_id: int, openid: str, db: Session = Depends(get_db)):
    """获取单条记录详情"""
    record = db.query(Record).filter(
        Record.id == record_id,
        Record.openid == openid
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    return record


@router.post("/", response_model=RecordResponse)
def create_record(record: RecordCreate, openid: str, db: Session = Depends(get_db)):
    """创建新记录"""
    # 检查数量限制
    count, limit = check_record_limit(openid, db)
    if count >= limit:
        raise HTTPException(
            status_code=400,
            detail=f"记录数量已达上限({limit}条)，请升级会员"
        )
    
    new_record = Record(
        openid=openid,
        type=record.type,
        name=record.name,
        group_type=record.group_type,
        date_type=record.date_type,
        month=record.month,
        day=record.day,
        year=record.year,
        remind_type=record.remind_type,
        sms_remind=record.sms_remind
    )
    
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    
    return new_record


@router.put("/{record_id}", response_model=RecordResponse)
def update_record(
    record_id: int,
    openid: str,
    update_data: RecordUpdate,
    db: Session = Depends(get_db)
):
    """更新记录"""
    record = db.query(Record).filter(
        Record.id == record_id,
        Record.openid == openid
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    # 更新非空字段
    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(record, field, value)
    
    db.commit()
    db.refresh(record)
    
    return record


@router.delete("/{record_id}")
def delete_record(record_id: int, openid: str, db: Session = Depends(get_db)):
    """删除记录"""
    record = db.query(Record).filter(
        Record.id == record_id,
        Record.openid == openid
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    db.delete(record)
    db.commit()
    
    return {"message": "删除成功"}


@router.post("/batch_import")
def batch_import_records(openid: str, items: List[dict], group_type: int = 1, db: Session = Depends(get_db)):
    """批量导入记录"""
    # 检查数量限制
    count, limit = check_record_limit(openid, db)
    
    imported = []
    failed = []
    
    for item in items:
        if count + len(imported) >= limit:
            failed.append({"item": item, "reason": "已达记录上限"})
            continue
        
        date_str = item.get("date", "")
        name = item.get("name", "")
        is_lunar = item.get("lunar", False)
        record_type = item.get("type", 1)
        
        # 解析日期
        if is_lunar:
            result = parse_lunar_date(date_str)
        else:
            result = parse_solar_date(date_str)
        
        if not result:
            failed.append({"item": item, "reason": "日期格式错误"})
            continue
        
        month, day = result
        
        new_record = Record(
            openid=openid,
            type=record_type,
            name=name,
            group_type=group_type,
            date_type=2 if is_lunar else 1,
            month=month,
            day=day
        )
        
        db.add(new_record)
        imported.append(item)
    
    db.commit()
    
    return {
        "imported": len(imported),
        "failed": len(failed),
        "details": failed
    }
