"""
时光记 - 订单支付API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
import hashlib

from database import get_db
from models import Order, User
from schemas import OrderCreate, OrderResponse

router = APIRouter(prefix="/api/order", tags=["订单"])


# 会员价格配置
VIP_PRICES = {
    1: 9.9,   # 年卡
    2: 39.9   # 终身
}

VIP_NAMES = {
    1: "年卡会员",
    2: "终身会员"
}


def generate_order_no() -> str:
    """生成订单号"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = str(uuid.uuid4()).replace("-", "")[:8].upper()
    return f"LIGHT{timestamp}{unique_id}"


@router.post("/create", response_model=OrderResponse)
def create_order(openid: str, order_data: OrderCreate, db: Session = Depends(get_db)):
    """创建订单"""
    # 验证用户
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 检查是否已是终身会员
    if user.vip_type == 2:
        raise HTTPException(status_code=400, detail="您已是终身会员，无需重复购买")
    
    # 年卡用户不能重复购买年卡
    if order_data.pay_type == 1 and user.vip_type == 1:
        raise HTTPException(status_code=400, detail="您已是年卡会员，请等待到期后再续费")
    
    pay_type = order_data.pay_type
    if pay_type not in VIP_PRICES:
        raise HTTPException(status_code=400, detail="无效的会员类型")
    
    # 创建订单
    order = Order(
        order_no=generate_order_no(),
        openid=openid,
        pay_type=pay_type,
        amount=VIP_PRICES[pay_type],
        pay_status=0
    )
    
    db.add(order)
    db.commit()
    db.refresh(order)
    
    return order


@router.get("/list")
def get_orders(openid: str, db: Session = Depends(get_db)):
    """获取用户订单列表"""
    orders = db.query(Order).filter(
        Order.openid == openid
    ).order_by(Order.created_at.desc()).all()
    
    return [{
        "id": o.id,
        "order_no": o.order_no,
        "pay_type": o.pay_type,
        "pay_type_name": VIP_NAMES.get(o.pay_type, "未知"),
        "amount": float(o.amount),
        "pay_status": o.pay_status,
        "pay_status_name": "已支付" if o.pay_status else "未支付",
        "pay_time": o.pay_time,
        "created_at": o.created_at
    } for o in orders]


@router.post("/pay/callback")
def pay_callback(order_no: str, db: Session = Depends(get_db)):
    """
    支付回调接口（简化版）
    实际生产环境需要验证微信支付签名
    """
    order = db.query(Order).filter(Order.order_no == order_no).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    if order.pay_status == 1:
        return {"message": "订单已处理"}
    
    # 更新订单状态
    order.pay_status = 1
    order.pay_time = datetime.now()
    
    # 更新用户会员状态
    user = db.query(User).filter(User.openid == order.openid).first()
    if user:
        if order.pay_type == 1:  # 年卡
            user.vip_type = 1
            from datetime import timedelta
            if user.vip_expire_time and user.vip_expire_time > datetime.now():
                # 累加年份
                user.vip_expire_time = user.vip_expire_time + timedelta(days=365)
            else:
                user.vip_expire_time = datetime.now() + timedelta(days=365)
        elif order.pay_type == 2:  # 终身
            user.vip_type = 2
            user.vip_expire_time = None  # 永久有效
            user.sms_count = 999999  # 无限短信
        
        # 增加短信条数
        if order.pay_type in [1, 2]:
            user.sms_count = 999999 if user.vip_type == 2 else user.sms_count
    
    db.commit()
    
    return {"message": "支付成功"}


@router.post("/query")
def query_order_status(order_no: str, db: Session = Depends(get_db)):
    """查询订单状态"""
    order = db.query(Order).filter(Order.order_no == order_no).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    return {
        "order_no": order.order_no,
        "pay_status": order.pay_status,
        "pay_type": order.pay_type,
        "amount": float(order.amount)
    }
