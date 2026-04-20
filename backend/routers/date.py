"""
时光记 - 日期相关API
"""
from fastapi import APIRouter
from datetime import datetime
from lunar_python import Lunar, Solar

router = APIRouter(prefix="/api/date", tags=["日期"])


@router.get("/now")
def get_current_date():
    """获取当前日期信息，包括农历"""
    print(datetime.now())
    now = datetime.now()
    solar = Solar.fromDate(now)
    lunar = solar.getLunar()
    
    return {
        "code": 200,
        "message": "success",
        "data": {
            "solar": {
                "year": now.year,
                "month": now.month,
                "day": now.day,
                "hour": now.hour,
                "minute": now.minute,
                "second": now.second,
                "weekday": now.weekday() + 1  # 1=周一, 7=周日
            },
            "lunar": {
                "year": lunar.getYearInChinese(),  # 如"丙午年"
                "month": lunar.getMonthInChinese(),  # 如"三月"
                "day": lunar.getDayInChinese()  # 如"初四"
            }
        }
    }
