from typing import Optional


def get_odds_system_name(match_league: str, euro_return_rate: float) -> Optional[str]:
    """根据联赛和欧指返还率获取对应的欧指赔率体系"""

    if euro_return_rate < 88.2 or euro_return_rate > 96.19:
        return None
    # 每个区间宽度：1，offset 0.8 让区间精准对应
    # 起始区间：88.2 对应体系 89
    # 所以 (88.2 + 0.8 → 89), (89.19 + 0.8 → 89),
    # (89.2 + 0.8 → 90), (90.19 + 0.8 → 90),...
    system_no = int(euro_return_rate + 0.8)

    league_map = {
        "英超": "英超",
        "西甲": "西甲",
        "法甲": "法甲",
        "意甲": "意甲",
        "德甲": "德甲",
    }

    system_name = league_map.get(match_league, "通用")

    return f"{system_name}{system_no}"
