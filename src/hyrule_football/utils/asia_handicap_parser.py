import re

CN_NUM_MAP = {
    "零": 0, "〇": 0,
    "一": 1, "二": 2, "两": 2,
    "三": 3, "四": 4, "五": 5,
    "六": 6, "七": 7, "八": 8,
    "九": 9, "十": 10
}

def cn_to_int(cn: str) -> int:
    """支持 0~20 的中文数字，例如 十五、十三、十九"""
    if cn == "十":
        return 10
    if len(cn) == 2 and cn[0] == "十":    # 十三→13
        return 10 + CN_NUM_MAP[cn[1]]
    if len(cn) == 2 and cn[1] == "十":    # 三十（扩展）
        return CN_NUM_MAP[cn[0]] * 10
    if len(cn) == 3 and cn[1] == "十":    # 二十三→23
        return CN_NUM_MAP[cn[0]] * 10 + CN_NUM_MAP[cn[2]]
    return CN_NUM_MAP.get(cn, None)


# ---------------------------------------------
# 解析单段盘口，例如：五球半、球半、十五球、两球半
# ---------------------------------------------
def parse_single_part(part: str) -> float:
    part = part.strip()

    # 特殊：球半 → 一球半 = 1.5
    if part == "球半":
        return 1.5

    # 特殊：平半 → 0.25, 半球 → 0.5
    special_single = {
        "平": 0.0,
        "平手": 0.0,
        "平球": 0.0,
        "平半": 0.25,
        "半平": 0.25,
        "半": 0.5,
        "半球": 0.5,
    }
    if part in special_single:
        return special_single[part]

    # 正常“X球”结构
    m = re.match(r"([零〇一二两三四五六七八九十]+)球(半)?", part)
    if m:
        num_cn = m.group(1)
        half = m.group(2) is not None

        num = cn_to_int(num_cn)
        if num is None:
            raise ValueError(f"无法识别数字: {num_cn}")

        if not (0 <= num <= 20):
            raise ValueError(f"球数超出范围: {num}")

        v = float(num)
        if half:
            v += 0.5
        return v

    raise ValueError(f"无法识别盘口片段: {part}")


# ---------------------------------------------
# 主入口：支持受让、分盘、所有写法
# ---------------------------------------------
def parse_asia_handicap_smart(hdp: str) -> float:
    s = hdp.strip()

    # -----------------------
    # 判断受让
    # -----------------------
    sign = 1 if s.startswith("受") else -1
    s = s.replace("受", "").replace("让", "")

    # -----------------------
    # 分盘： X/Y
    # 包含：平/半、平手/半球、球半/两球、半球/一球...
    # -----------------------
    if "/" in s:
        parts = s.split("/")
        values = [parse_single_part(p) for p in parts]
        return sign * (sum(values) / len(values))

    # -----------------------
    # 单盘口（不含 /）
    # -----------------------
    return sign * parse_single_part(s)
