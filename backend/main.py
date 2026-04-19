"""
时光记 - FastAPI 主应用
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import logging

from database import engine, Base, SessionLocal
from routers import user, record, blessing, order, sms
from tasks import check_reminders, check_vip_expire

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建 FastAPI 应用
app = FastAPI(
    title="时光记 API",
    description="时光记小程序后端API服务",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(user.router)
app.include_router(record.router)
app.include_router(blessing.router)
app.include_router(order.router)
app.include_router(sms.router)


# 健康检查
@app.get("/health")
def health_check():
    return {"status": "ok", "time": datetime.now().isoformat()}


# 首页
@app.get("/")
def root():
    return {
        "name": "时光记 API",
        "version": "1.0.0",
        "description": "记住每一个重要日子"
    }


# 定时任务调度器
scheduler = AsyncIOScheduler()


def run_daily_tasks():
    """执行每日定时任务"""
    db = SessionLocal()
    try:
        check_reminders(db)
        check_vip_expire(db)
        logger.info("定时任务执行完成")
    finally:
        db.close()


# 添加定时任务
scheduler.add_job(
    run_daily_tasks,
    'cron',
    hour=8,
    minute=0,
    id='daily_reminder_check'
)


@app.on_event("startup")
async def startup_event():
    """应用启动时"""
    scheduler.start()
    logger.info("定时任务调度器已启动")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时"""
    scheduler.shutdown()
    logger.info("定时任务调度器已关闭")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
