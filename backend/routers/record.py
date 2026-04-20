"""
时光记 - 生日/纪念日记录API (RESTful)
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from calendar import monthrange

from database import get_db
from models import Record, User
from schemas import RecordCreate, RecordUpdate, RecordResponse, BatchImportRequest, ApiResponse
from routers.user import get_current_user
from utils.response import success
from utils.lunar import parse_lunar_date, parse_solar_date
from lunar_python import Lunar, Solar

router = APIRouter(prefix="/api/records", tags=["记录"])

# 农历月份中文
LUNAR_MONTHS = {
    1: "正月", 2: "二月", 3: "三月", 4: "四月", 5: "五月", 6: "六月",
    7: "七月", 8: "八月", 9: "九月", 10: "十月", 11: "冬月", 12: "腊月"
}

# 农历日期中文
LUNAR_DAYS = {
    1: "初一", 2: "初二", 3: "初三", 4: "初四", 5: "初五",
    6: "初六", 7: "初七", 8: "初八", 9: "初九", 10: "初十",
    11: "十一", 12: "十二", 13: "十三", 14: "十四", 15: "十五",
    16: "十六", 17: "十七", 18: "十八", 19: "十九", 20: "二十",
    21: "廿一", 22: "廿二", 23: "廿三", 24: "廿四", 25: "廿五",
    26: "廿六", 27: "廿七", 28: "廿八", 29: "廿九", 30: "三十"
}


def check_record_limit(openid: str, db: Session) -> tuple:
    """检查记录数量限制"""
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    record_count = db.query(Record).filter(Record.openid == openid).count()
    limits = {0: 8, 1: 100, 2: 100}
    limit = limits.get(user.vip_type, 8)
    
    return record_count, limit


@router.get("/", response_model=ApiResponse)
def get_records(
    group_type: Optional[int] = None,
    date_type: Optional[int] = None,
    days: Optional[int] = Query(default=None, ge=1, le=365, description="即将到来的天数"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取记录列表
    GET /api/records
    GET /api/records?group_type=1
    GET /api/records?days=14  # 即将到来的记录
    """
    query = db.query(Record).filter(Record.openid == current_user.openid)
    
    if group_type:
        query = query.filter(Record.group_type == group_type)
    if date_type:
        query = query.filter(Record.date_type == date_type)
    
    records = query.order_by(Record.month, Record.day).all()
    
    # 如果指定了 days 参数，返回即将到来的记录
    if days:
        now = datetime.now()
        today_solar = Solar.fromDate(now)
        today_lunar = today_solar.getLunar()
        upcoming = []
        
        for record in records:
            if record.date_type == 2:
                # 农历日期计算
                try:
                    # 构建农历日期（今年）
                    lunar_birthday = Lunar.fromYmd(
                        today_lunar.getYear(),
                        record.month,
                        record.day
                    )
                    # 转为阳历日期
                    solar_birthday = lunar_birthday.getSolar()
                    
                    # 判断是否今年已过（只判断是否在今天之前，今天不算过）
                    if solar_birthday.isBefore(today_solar):
                        # 已过，转到下一年
                        lunar_birthday = Lunar.fromYmd(
                            today_lunar.getYear() + 1,
                            record.month,
                            record.day
                        )
                        solar_birthday = lunar_birthday.getSolar()
                    
                    # 计算天数差距
                    days_until = solar_birthday.subtract(today_solar)
                except:
                    continue
            else:
                # 公历日期计算
                today = now.replace(hour=0, minute=0, second=0, microsecond=0)
                today_date = (now.month, now.day)
                record_date = (record.month, record.day)
                
                if record_date > today_date:
                    # 今年还未到
                    _, days_in_month = monthrange(now.year, record.month)
                    target_date = datetime(now.year, record.month, min(record.day, days_in_month))
                    days_until = (target_date - today).days
                elif record_date == today_date:
                    # 今天（days_until = 0）
                    days_until = 0
                else:
                    # 今年已过，明年
                    _, days_in_month = monthrange(now.year + 1, record.month)
                    target_date = datetime(now.year + 1, record.month, min(record.day, days_in_month))
                    days_until = (target_date - today).days
            
            if 0 <= days_until <= days:
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
                    "year": record.year,
                    "days_until": days_until,
                    "age": age,
                    "lunar_display": "农历" if record.date_type == 2 else "",
                    "lunar_month_text": LUNAR_MONTHS.get(record.month, f"{record.month}月"),
                    "lunar_day_text": LUNAR_DAYS.get(record.day, f"{record.day}日")
                })
        
        upcoming.sort(key=lambda x: x["days_until"])
        return success(upcoming)
    
    return success([
        {
            "id": r.id,
            "name": r.name,
            "type": r.type,
            "month": r.month,
            "day": r.day,
            "group_type": r.group_type,
            "date_type": r.date_type,
            "year": r.year,
            "remind_type": r.remind_type,
            "sms_remind": r.sms_remind,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "lunar_month_text": LUNAR_MONTHS.get(r.month, f"{r.month}月"),
            "lunar_day_text": LUNAR_DAYS.get(r.day, f"{r.day}日")
        }
        for r in records
    ])


@router.get("/{record_id}", response_model=ApiResponse)
def get_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取单条记录详情
    GET /api/records/{id}
    """
    record = db.query(Record).filter(
        Record.id == record_id,
        Record.openid == current_user.openid
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    return success({
        "id": record.id,
        "name": record.name,
        "type": record.type,
        "month": record.month,
        "day": record.day,
        "group_type": record.group_type,
        "date_type": record.date_type,
        "year": record.year,
        "remind_type": record.remind_type,
        "sms_remind": record.sms_remind
    })


@router.post("/", response_model=ApiResponse)
def create_record(
    record_data: RecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建新记录
    POST /api/records
    """
    count, limit = check_record_limit(current_user.openid, db)
    if count >= limit:
        raise HTTPException(status_code=400, detail=f"记录数量已达上限({limit}条)")
    
    new_record = Record(
        openid=current_user.openid,
        type=record_data.type,
        name=record_data.name,
        group_type=record_data.group_type,
        date_type=record_data.date_type,
        month=record_data.month,
        day=record_data.day,
        year=record_data.year,
        remind_type=record_data.remind_type,
        sms_remind=record_data.sms_remind
    )
    
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    
    return success({
        "id": new_record.id,
        "name": new_record.name,
        "type": new_record.type,
        "month": new_record.month,
        "day": new_record.day,
        "group_type": new_record.group_type,
        "date_type": new_record.date_type
    }, "创建成功")


@router.post("/batch", response_model=ApiResponse)
def batch_create_records(
    request_data: BatchImportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    批量创建记录
    POST /api/records/batch
    """
    count, limit = check_record_limit(current_user.openid, db)
    
    imported = []
    failed = []
    
    for item in request_data.items:
        if count + len(imported) >= limit:
            failed.append({"item": item.model_dump(), "reason": "已达记录上限"})
            continue
        
        # 解析日期
        if item.lunar:
            result = parse_lunar_date(item.date)
        else:
            result = parse_solar_date(item.date)
        
        if not result:
            failed.append({"item": item.model_dump(), "reason": "日期格式错误"})
            continue
        
        month, day = result
        
        new_record = Record(
            openid=current_user.openid,
            type=item.type or 1,
            name=item.name,
            group_type=request_data.group_type,
            date_type=2 if item.lunar else 1,
            month=month,
            day=day
        )
        
        db.add(new_record)
        imported.append(item.model_dump())
    
    db.commit()
    
    return success({
        "imported": len(imported),
        "failed": len(failed),
        "details": failed
    }, "导入完成")


@router.put("/{record_id}", response_model=ApiResponse)
def update_record(
    record_id: int,
    update_data: RecordUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新记录
    PUT /api/records/{id}
    """
    record = db.query(Record).filter(
        Record.id == record_id,
        Record.openid == current_user.openid
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        # 处理 year 字段：空字符串转为 None
        if field == 'year' and value == '':
            value = None
        setattr(record, field, value)
    
    db.commit()
    db.refresh(record)
    
    return success({
        "id": record.id,
        "name": record.name,
        "type": record.type,
        "month": record.month,
        "day": record.day,
        "group_type": record.group_type,
        "date_type": record.date_type
    }, "更新成功")


@router.delete("/{record_id}", response_model=ApiResponse)
def delete_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除记录
    DELETE /api/records/{id}
    """
    record = db.query(Record).filter(
        Record.id == record_id,
        Record.openid == current_user.openid
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    db.delete(record)
    db.commit()
    
    return success(None, "删除成功")
