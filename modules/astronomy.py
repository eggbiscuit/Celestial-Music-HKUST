from astropy.time import Time
from astropy.coordinates import get_sun, EarthLocation, BarycentricTrueEcliptic, ICRS
import astropy.units as u
import pytz
import logging
import numpy as np
import zhdate
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# 28星宿按传统顺序
MANSIONS = [
    "角", "亢", "氐", "房", "心", "尾", "箕", # 东方青龙
    "斗", "牛", "女", "虚", "危", "室", "壁", # 北方玄武
    "奎", "娄", "胃", "昴", "毕", "觜", "参", # 西方白虎
    "井", "鬼", "柳", "星", "张", "翼", "轸"  # 南方朱雀
]

# 十二星次与节气的对应关系
TWELVE_ZODIAC_SIGNS = {
    "玄枵": {"start": 300, "end": 330, "solar_term": "小寒/大寒", "mansions": ["女", "虚", "危"]},
    "娵訾": {"start": 330, "end": 360, "solar_term": "立春/雨水", "mansions": ["室", "壁"]}, 
    "降娄": {"start": 0,   "end": 30,  "solar_term": "惊蛰/春分", "mansions": ["奎", "娄"]},
    "大梁": {"start": 30,  "end": 60,  "solar_term": "清明/谷雨", "mansions": ["胃", "昴", "毕"]},
    "实沈": {"start": 60,  "end": 90,  "solar_term": "立夏/小满", "mansions": ["觜", "参"]},
    "鹑首": {"start": 90,  "end": 120, "solar_term": "芒种/夏至", "mansions": ["井", "鬼"]},
    "鹑火": {"start": 120, "end": 150, "solar_term": "小暑/大暑", "mansions": ["柳", "星", "张"]},
    "鹑尾": {"start": 150, "end": 180, "solar_term": "立秋/处暑", "mansions": ["翼", "轸"]},
    "寿星": {"start": 180, "end": 210, "solar_term": "白露/秋分", "mansions": ["角", "亢"]},
    "大火": {"start": 210, "end": 240, "solar_term": "寒露/霜降", "mansions": ["氐", "房", "心"]},
    "析木": {"start": 240, "end": 270, "solar_term": "立冬/小雪", "mansions": ["尾", "箕"]},
    "星纪": {"start": 270, "end": 300, "solar_term": "冬至/大雪", "mansions": ["斗", "牛"]}
}



def convert_lunar_to_solar(year, month, day):
    """农历转公历"""
    try:
        lunar_date = zhdate.ZhDate(year, month, day)
        solar_date = lunar_date.to_datetime()
        return solar_date.year, solar_date.month, solar_date.day
    except Exception as e:
        logger.error(f"农历转换失败: {str(e)}")
        return year, month, day

def get_sun_position(timestamp, latitude, longitude):
    """计算太阳位置和黄经"""
    try:
        if isinstance(timestamp, (int, float)):
            # 如果是时间戳，先转换为datetime再转ISO字符串
            dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
            time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
            time = Time(time_str, format='iso', scale='utc')
        elif isinstance(timestamp, str):
            time = Time(timestamp, format='iso', scale='utc')
        else:
            time = Time(timestamp)
        
        location = EarthLocation(lat=latitude*u.deg, lon=longitude*u.deg)
        sun = get_sun(time)
        
        # 地心坐标系计算
        ecliptic_longitude = sun.geocentrictrueecliptic.lon.degree % 360
        
        # ✅ 可选：添加观测者位置相关计算
        # sun_altaz = sun.transform_to(AltAz(obstime=time, location=location))
        
        result = {
            'ra': float(sun.ra.deg),
            'dec': float(sun.dec.deg),  # ✅ 修正
            'ecliptic_longitude': ecliptic_longitude,
            'ecliptic_latitude': float(sun.geocentrictrueecliptic.lat.degree),
            'distance': float(sun.distance.km),
            'timestamp': time.iso,
            # ✅ 可选：添加本地观测信息
            # 'altitude': float(sun_altaz.alt.deg),  # 太阳高度角
            # 'azimuth': float(sun_altaz.az.deg),    # 太阳方位角
            # 'observer_lat': latitude,
            # 'observer_lon': longitude
        }
        
        logger.info(f"太阳黄经计算成功: {result['ecliptic_longitude']:.2f}°")
        return result
        
    except Exception as e:
        logger.error(f"太阳位置计算失败: {str(e)}")
        return {
            'ra': 0.0, 'dec': 0.0, 'ecliptic_longitude': 0.0,
            'ecliptic_latitude': 0.0, 'distance': 149597870.7,
            'timestamp': str(timestamp), 'error': str(e)
        }

def match_zodiac_sign_interval(longitude):
    """匹配十二星次区间"""
    try:
        lon = float(longitude) % 360
        
        for sign_name, sign_data in TWELVE_ZODIAC_SIGNS.items():
            start, end = sign_data["start"], sign_data["end"]
            
            # 处理跨0度的情况
            if start > end:  # 如娵訾 330-360度
                if lon >= start or lon < end:
                    return sign_name, sign_data
            else:
                if start <= lon < end:
                    return sign_name, sign_data
        
        return "玄枵", TWELVE_ZODIAC_SIGNS["玄枵"]
        
    except Exception as e:
        logger.error(f"星次区间匹配失败: {str(e)}")
        return "玄枵", TWELVE_ZODIAC_SIGNS["玄枵"]

def determine_solar_term(zodiac_data, precise_longitude):
    """确定对应节气 - 天文精确版本"""
    
    # 24节气的标准天文黄经 (基于太阳视黄经)
    SOLAR_TERMS_LONGITUDE = {
        "春分": 0,   "清明": 15,  "谷雨": 30,
        "立夏": 45,  "小满": 60,  "芒种": 75,
        "夏至": 90,  "小暑": 105, "大暑": 120,
        "立秋": 135, "处暑": 150, "白露": 165,
        "秋分": 180, "寒露": 195, "霜降": 210,
        "立冬": 225, "小雪": 240, "大雪": 255,
        "冬至": 270, "小寒": 285, "大寒": 300,
        "立春": 315, "雨水": 330, "惊蛰": 345
    }
    
    lon = float(precise_longitude) % 360
    
    # 找到已过的最近节气和即将到来的节气
    passed_terms = []
    upcoming_terms = []
    
    for term, term_lon in SOLAR_TERMS_LONGITUDE.items():
        if term_lon <= lon:
            passed_terms.append((term, term_lon, lon - term_lon))
        else:
            upcoming_terms.append((term, term_lon, term_lon - lon))
    
    # 处理跨年边界情况
    if lon > 315:  # 立春之后
        upcoming_terms.append(("春分", 360, 360 - lon))
    
    # 找到最近的已过节气和即将到来的节气
    if passed_terms:
        latest_passed = max(passed_terms, key=lambda x: x[1])
        passed_term, passed_lon, passed_diff = latest_passed
    else:
        passed_term, passed_lon, passed_diff = None, None, None
    
    if upcoming_terms:
        next_upcoming = min(upcoming_terms, key=lambda x: x[2])
        upcoming_term, upcoming_lon, upcoming_diff = next_upcoming
    else:
        upcoming_term, upcoming_lon, upcoming_diff = None, None, None
    
    # 生成描述性节气信息
    if passed_term and upcoming_term:
        if passed_diff < upcoming_diff:
            result = f"{passed_term}后期"
        else:
            result = f"接近{upcoming_term}"
        detail = f"{passed_term}已过 → 向{upcoming_term}前进"
    elif passed_term:
        result = f"{passed_term}后期"
        detail = f"{passed_term}已过"
    elif upcoming_term:
        result = f"接近{upcoming_term}"
        detail = f"向{upcoming_term}前进"
    else:
        result = "春分"
        detail = "春分时期"
    
    logger.info(f"🌱 精确节气匹配: {lon:.2f}° → {result} [{detail}]")
    return result

def get_28_mansions_for_display(zodiac_data):
    """获取对应的二十八星宿（用于显示）"""
    return zodiac_data.get("mansions", [])

def generate_solar_term_music_prompt(solar_term, zodiac_sign, duration=45):
    """生成节气音乐提示词"""
    try:
        # 节气音乐风格映射
        solar_term_styles = {
            "立春": "bright, energetic, new beginnings",
            "雨水": "gentle, flowing, refreshing", 
            "惊蛰": "awakening, thunderous, dynamic",
            "春分": "balanced, harmonious, peaceful",
            "清明": "clear, serene, contemplative",
            "谷雨": "nurturing, growth, organic",
            "立夏": "warm, passionate, vibrant",
            "小满": "abundant, flourishing, rich",
            "芒种": "busy, productive, rhythmic",
            "夏至": "intense, powerful, climactic", 
            "小暑": "warm, comfortable, gentle",
            "大暑": "hot, intense, fiery",
            "立秋": "cooling, transitional, nostalgic",
            "处暑": "relieving, peaceful, settling",
            "白露": "crystalline, pure, delicate",
            "秋分": "balanced, reflective, mature",
            "寒露": "cool, crisp, clear",
            "霜降": "chilly, preparing, anticipatory",
            "立冬": "quiet, introspective, still",
            "小雪": "gentle, soft, ethereal",
            "大雪": "heavy, profound, deep",
            "冬至": "minimal, essential, turning point",
            "小寒": "cold, stark, enduring", 
            "大寒": "frozen, crystalline, waiting"
        }
        
        style = solar_term_styles.get(solar_term, "seasonal, atmospheric")
        
        prompt = (f"Traditional Chinese music inspired by {solar_term} solar term, "
                 f"{style}, {zodiac_sign} zodiac influence, "
                 f"{duration} seconds duration, "
                 f"cinematic orchestral arrangement")
        
        logger.info(f"生成节气音乐提示词: {solar_term} - {prompt}")
        return prompt
        
    except Exception as e:
        logger.error(f"音乐提示词生成失败: {str(e)}")
        return f"Traditional Chinese seasonal music, {duration} seconds"

def get_all_mansions_positions(timestamp):
    """获取所有星宿位置（用于Three.js可视化）"""
    try:
        positions = {}
        for i, mansion in enumerate(MANSIONS):
            ecliptic_lon = i * (360.0 / 28)
            positions[mansion] = {
                'ecliptic_longitude': ecliptic_lon,
                'index': i
            }
        return positions
    except Exception as e:
        logger.error(f"星宿位置计算失败: {str(e)}")
        return {}

# 保留兼容性函数
def get_moon_position(timestamp, latitude, longitude):
    """废弃函数，保留兼容性"""
    logger.warning("get_moon_position已废弃，请使用get_sun_position")
    return get_sun_position(timestamp, latitude, longitude)

def calc_mansion(ecliptic_longitude):
    """废弃函数，保留兼容性"""
    logger.warning("calc_mansion已废弃")
    zodiac_sign, zodiac_data = match_zodiac_sign_interval(ecliptic_longitude)
    mansions = get_28_mansions_for_display(zodiac_data)
    return mansions[0] if mansions else "虚"
