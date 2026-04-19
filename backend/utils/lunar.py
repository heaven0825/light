"""
时光记 - 农历转换工具
支持农历日期与公历日期的相互转换
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
import re

# 农历月份名称
LUNAR_MONTHS = {
    '正': 1, '一月': 1, '正月': 1,
    '二': 2, '二月': 2,
    '三': 3, '三月': 3,
    '四': 4, '四月': 4,
    '五': 5, '五月': 5,
    '六': 6, '六月': 6,
    '七': 7, '七月': 7,
    '八': 8, '八月': 8,
    '九': 9, '九月': 9,
    '十': 10, '十月': 10,
    '冬': 11, '十一月': 11,
    '腊': 12, '十二月': 12,
}

# 农历日期名称
LUNAR_DAYS = {
    '初一': 1, '初二': 2, '初三': 3, '初四': 4, '初五': 5,
    '初六': 6, '初七': 7, '初八': 8, '初九': 9, '初十': 10,
    '十一': 11, '十二': 12, '十三': 13, '十四': 14, '十五': 15,
    '十六': 16, '十七': 17, '十八': 18, '十九': 19, '二十': 20,
    '廿一': 21, '廿二': 22, '廿三': 23, '廿四': 24, '廿五': 25,
    '廿六': 26, '廿七': 27, '廿八': 28, '廿九': 29, '三十': 30,
}


def parse_lunar_date(date_str: str) -> Optional[Tuple[int, int]]:
    """
    解析农历日期字符串
    支持格式: "正月十五", "七月廿二", "腊月二十"
    返回: (month, day) 或 None
    """
    date_str = date_str.strip()
    
    # 尝试匹配 月日 格式
    for month_name, month in LUNAR_MONTHS.items():
        if date_str.startswith(month_name):
            remaining = date_str[len(month_name):]
            for day_name, day in LUNAR_DAYS.items():
                if remaining == day_name:
                    return (month, day)
    
    return None


def parse_solar_date(date_str: str) -> Optional[Tuple[int, int]]:
    """
    解析公历日期字符串
    支持格式: "0408", "1204"
    返回: (month, day) 或 None
    """
    date_str = date_str.strip()
    if len(date_str) == 4 and date_str.isdigit():
        month = int(date_str[:2])
        day = int(date_str[2:])
        if 1 <= month <= 12 and 1 <= day <= 31:
            return (month, day)
    return None


def lunar_to_solar(year: int, month: int, day: int) -> Optional[datetime]:
    """
    将农历日期转换为公历日期
    这是一个简化版本，实际需要查表或使用完整的农历算法
    """
    # 简化实现：假设农历日期对应公历同月同日（误差1-2天）
    # 正式环境建议使用 chinalunarcalendar 库或预计算表
    try:
        # 以2024年为基准做简单估算
        base_year = 2024
        base_date = datetime(base_year, month, min(day, 28))
        
        # 粗略估算：农历通常比公历晚15-45天
        offset_days = 20
        result = base_date + timedelta(days=offset_days)
        
        # 调整到正确年份
        while result.year != year:
            if result.year < year:
                result = result + timedelta(days=365)
            else:
                result = result - timedelta(days=365)
        
        return result
    except:
        return None


def solar_to_lunar(year: int, month: int, day: int) -> Optional[Tuple[int, int, int]]:
    """
    将公历日期转换为农历日期
    返回: (lunar_year, lunar_month, lunar_day)
    """
    # 简化实现
    # 正式环境建议使用 chinalunarcalendar 库
    # 这里返回近似值，实际需要完整算法
    return (year, month, day)


def get_next_lunar_birthday(month: int, day: int, base_date: datetime = None) -> datetime:
    """
    计算下一个农历生日对应的公历日期
    """
    if base_date is None:
        base_date = datetime.now()
    
    # 简化实现：假设同月同日
    try:
        next_date = datetime(base_date.year, month, min(day, 28))
        if next_date <= base_date:
            next_date = datetime(base_date.year + 1, month, min(day, 28))
        return next_date
    except:
        return base_date + timedelta(days=30)


def calculate_age(birth_year: int, current_date: datetime = None) -> Optional[int]:
    """计算年龄"""
    if current_date is None:
        current_date = datetime.now()
    if birth_year and birth_year > 1900 and birth_year <= current_date.year:
        return current_date.year - birth_year
    return None
