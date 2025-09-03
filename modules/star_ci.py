"""
十二星次模块
处理太阳位置与十二星次的对应关系
"""

# 十二星次与五行的对应关系
STAR_CI_ELEMENT_MAP = {
    "星纪": "Water",    # 水 - 北方玄武
    "玄枵": "Water",    # 水 - 北方玄武  
    "娵訾": "Water",    # 水 - 北方玄武
    "降娄": "Metal",    # 金 - 西方白虎
    "大梁": "Metal",    # 金 - 西方白虎
    "实沈": "Metal",    # 金 - 西方白虎
    "鹑首": "Fire",     # 火 - 南方朱雀
    "鹑火": "Fire",     # 火 - 南方朱雀
    "鹑尾": "Fire",     # 火 - 南方朱雀
    "寿星": "Wood",     # 木 - 东方青龙
    "大火": "Wood",     # 木 - 东方青龙
    "析木": "Wood"      # 木 - 东方青龙
}

def get_element_from_star_ci(star_ci: str) -> str:
    """
    根据十二星次获取对应的五行
    """
    return STAR_CI_ELEMENT_MAP.get(star_ci, "Wood")

def get_star_ci_info(star_ci: str) -> dict:
    """
    获取十二星次的详细信息
    """
    from modules.astronomy import STAR_RANGES, STAR_TO_MANSIONS
    
    return {
        "name": star_ci,
        "element": get_element_from_star_ci(star_ci),
        "longitude_range": STAR_RANGES.get(star_ci, (0, 30)),
        "corresponding_mansions": STAR_TO_MANSIONS.get(star_ci, ["角"])
    }
