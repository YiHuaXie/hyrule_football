def water_level_standadrd_str(input: str | float) -> str:
    """标准化亚盘水位"""
    float_input = 0.0
    if isinstance(input, str):
        float_input = float(input)
    elif isinstance(input, float):
        float_input = input
    else:
        raise ValueError(f"❌ 无法识别的水位值: {input}")

    if float_input < 1:
        raise ValueError(f"❌ 水位值必须大于 1.0: {input}")
    elif float_input < 1.9:
        return "低"
    elif float_input < 1.95:
        return "高"
    else:
        return "中"

def opposite_water_level(level: str) -> str:
    """高 / 中 / 低 的反义词转换"""

    mapping = {
        "高": "低",
        "低": "高",
        "中": "中",   # 中的反义还是中
        "高中": "低中",
        "低中": "高中",
    }

    return mapping.get(level, "未知级别")