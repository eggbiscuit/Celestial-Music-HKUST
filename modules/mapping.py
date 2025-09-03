import random

ELEMENT_MUSIC_MAP = {
    "Wood": {
        "instruments": ["Strings", "Flute", "Harp", "Acoustic Guitar"],
        "modes": ["Dorian", "Mixolydian", "Natural Minor"],
        "mood": ["peaceful", "flowing", "natural", "organic"],
        "tempo_range": [60, 90],
        "duration_style": "flowing and organic progression"
    },
    "Fire": {
        "instruments": ["Trumpet", "Brass", "Percussion", "Electric Guitar"],
        "modes": ["Phrygian", "Harmonic Minor", "Lydian Dominant"],
        "mood": ["passionate", "energetic", "intense", "blazing"],
        "tempo_range": [120, 160],
        "duration_style": "building intensity throughout"
    },
    "Earth": {
        "instruments": ["Piano", "Organ", "Bass", "Timpani"],
        "modes": ["Ionian", "Aeolian", "Mixolydian"],
        "mood": ["stable", "grounding", "nurturing", "solid"],
        "tempo_range": [70, 100],
        "duration_style": "steady and grounding"
    },
    "Metal": {
        "instruments": ["Bells", "Flute", "Glockenspiel", "Chimes"],
        "modes": ["Lydian", "Mixolydian", "Major Pentatonic"],
        "mood": ["clear", "bright", "crystalline", "resonant"],
        "tempo_range": [90, 120],
        "duration_style": "clear and resonant with gentle evolution"
    },
    "Water": {
        "instruments": ["Synthesizer", "Ambient Pads", "Flute", "Cello"],
        "modes": ["Aeolian", "Phrygian", "Dorian"],
        "mood": ["mysterious", "flowing", "deep", "meditative"],
        "tempo_range": [50, 80],
        "duration_style": "fluid and mysterious with gradual development"
    }
}

def map_to_params(element: str) -> tuple:
    """将五行元素映射为音乐参数"""
    mapping = ELEMENT_MUSIC_MAP.get(element, ELEMENT_MUSIC_MAP["Wood"])
    instrument = random.choice(mapping["instruments"])
    mode = random.choice(mapping["modes"])
    return (instrument, mode)

def get_full_music_config(element: str, duration: int = 45) -> dict:
    """获取包含时长信息的完整音乐配置"""
    mapping = ELEMENT_MUSIC_MAP.get(element, ELEMENT_MUSIC_MAP["Wood"])
    return {
        "element": element,
        "available_instruments": mapping["instruments"],
        "available_modes": mapping["modes"],
        "mood_descriptors": mapping["mood"],
        "tempo_range": mapping["tempo_range"],
        "duration": duration,
        "duration_style": mapping["duration_style"],
        "suggested_structure": get_duration_structure(duration)
    }

def get_duration_structure(duration: int) -> dict:
    """根据时长建议音乐结构"""
    if duration <= 30:
        return {
            "intro": "0-5s",
            "main": "5-25s",
            "outro": "25-30s",
            "structure": "Simple A-B-A form"
        }
    elif duration <= 60:
        return {
            "intro": "0-8s",
            "verse": "8-20s",
            "bridge": "20-35s",
            "verse_repeat": "35-50s",
            "outro": "50-60s",
            "structure": "Extended A-B-A-B-C form"
        }
    else:
        return {
            "intro": "0-10s",
            "development": "10-40s",
            "climax": "40-50s",
            "resolution": "50-60s+",
            "structure": "Full development form"
        }

def create_enhanced_prompt(instrument: str, mode: str, element: str, style: str = "cinematic, ethereal", duration: int = 45) -> str:
    """创建包含时长和结构的增强型prompt"""
    mapping = ELEMENT_MUSIC_MAP.get(element, ELEMENT_MUSIC_MAP["Wood"])
    mood = random.choice(mapping["mood"])
    duration_style = mapping["duration_style"]
    
    # 根据时长调整描述
    if duration <= 30:
        length_desc = "concise"
    elif duration <= 60:
        length_desc = "medium-length"
    else:
        length_desc = "extended"
    
    prompt = f"{instrument}, {mode} mode, {style}, {mood} atmosphere, {length_desc} {duration}-second composition with {duration_style}, complete musical piece with clear beginning and ending"
    return prompt

# 新增：节气音乐配置函数
def get_solar_term_music_config(solar_term, zodiac_sign):
    """根据节气和星次获取音乐配置"""
    return {
        "solar_term": solar_term,
        "zodiac_sign": zodiac_sign,
        "instrument": "Traditional Chinese Orchestra",
        "mode": "Pentatonic",
        "style": "Traditional Chinese seasonal music"
    }
