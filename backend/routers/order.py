"""
时光记 - 订单API (RESTful)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from database import get_db
from models import Order, User
from schemas import OrderCreate, ApiResponse
from routers.user import get_current_user
from utils.response import success

router = APIRouter(prefix="/api/orders", tags=["订单"])


@router.post("/", response_model=ApiResponse)
def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建订单
    POST /api/orders
    """
    # 计算金额
    amounts = {1: 9.9, 2: 39.9}
    amount = amounts.get(order_data.pay_type, 0)
    
    # 生成订单号
    order_no = f"ORDER_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    order = Order(
        openid=current_user.openid,
        order_no=order_no,
        pay_type=order_data.pay_type,
        amount=amount,
        pay_status=0  # 待支付
    )
    
    db.add(order)
    db.commit()
    db.refresh(order)
    
    return success({
        "order_no": order.order_no,
        "pay_type": order.pay_type,
        "amount": order.amount,
        "pay_status": order.pay_status
    }, "订单创建成功")


@router.get("/", response_model=ApiResponse)
def get_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取订单列表
    GET /api/orders
    """
    orders = db.query(Order).filter(
        Order.openid == current_user.openid
    ).order_by(Order.created_at.desc()).all()
    
    return success([
        {
            "id": o.id,
            "order_no": o.order_no,
            "pay_type": o.pay_type,
            "amount": o.amount,
            "pay_status": o.pay_status,
            "pay_time": o.pay_time.isoformat() if o.pay_time else None,
            "created_at": o.created_at.isoformat() if o.created_at else None
        }
        for o in orders
    ])


@router.post("/pay", response_model=ApiResponse)
def pay_order(
    order_no: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    模拟支付回调
    POST /api/orders/pay?order_no=xxx
    """
    order = db.query(Order).filter(
        Order.order_no == order_no,
        Order.openid == current_user.openid
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    if order.pay_status == 1:
        return success(None, "订单已支付")
    
    # 模拟支付成功
    order.pay_status = 1
    order.pay_time = datetime.now()
    
    # 升级用户会员
    user = db.query(User).filter(User.openid == current_user.openid).first()
    if user:
        user.vip_type = order.pay_type  # 1=年卡, 2=终身
        if order.pay_type == 1:
            from datetime import timedelta
            user.vip_expire_time = datetime.now() + timedelta(days=365)
    
    db.commit()
    
    return success({"pay_status": 1}, "支付成功")
