"""
时光记 - Pydantic schemas
"""
from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


# ============ 通用 ============
class ApiResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: Optional[Any] = None


# ============ 用户相关 ============
class WxLoginRequest(BaseModel):
    code: str


class UserInfo(BaseModel):
    openid: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    openid: str
    nickname: Optional[str]
    avatar: Optional[str]
    vip_type: int
    vip_expire_time: Optional[datetime]
    sms_count: int

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    avatar: Optional[str] = None


# ============ 记录相关 ============
class RecordCreate(BaseModel):
    type: int = 1  # 1=生日 2=纪念日
    name: str
    group_type: int = 1  # 1=家人 2=朋友 3=同事 4=客户
    date_type: int = 1  # 1=公历 2=农历
    month: int
    day: int
    year: Optional[int] = None
    remind_type: Optional[str] = None
    sms_remind: int = 0


class RecordUpdate(BaseModel):
    type: Optional[int] = None
    name: Optional[str] = None
    group_type: Optional[int] = None
    date_type: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None
    year: Optional[int | str] = None  # 接受整数或空字符串
    remind_type: Optional[str] = None
    sms_remind: Optional[int] = None


class RecordResponse(BaseModel):
    id: int
    openid: str
    type: int
    name: str
    group_type: int
    date_type: int
    month: int
    day: int
    year: Optional[int]
    remind_type: Optional[str]
    sms_remind: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============ 祝福语相关 ============
class BlessingResponse(BaseModel):
    id: int
    group_type: int
    content: str

    class Config:
        from_attributes = True


# ============ 订单相关 ============
class OrderCreate(BaseModel):
    pay_type: int  # 1=年卡 2=终身会员


class OrderResponse(BaseModel):
    id: int
    order_no: str
    pay_type: int
    amount: float
    pay_status: int
    pay_time: Optional[datetime]

    class Config:
        from_attributes = True


# ============ 短信相关 ============
class SmsSendRequest(BaseModel):
    record_id: int
    mobile: str
    content: str


class SmsLogResponse(BaseModel):
    id: int
    record_id: int
    mobile: str
    content: str
    send_time: datetime
    status: int

    class Config:
        from_attributes = True


# ============ 批量导入 ============
class BatchImportItem(BaseModel):
    date: str
    name: str
    type: Optional[int] = 1
    lunar: Optional[bool] = False


class BatchImportRequest(BaseModel):
    items: List[BatchImportItem]
    group_type: int = 1
