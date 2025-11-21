from typing import Optional


def get_league_name(league_name: str) -> Optional[str]:
    league_map = {
        "英超": "英超",
        "西甲": "西甲",
        "法甲": "法甲",
        "意甲": "意甲",
        "德甲": "德甲",
    }

    return league_map.get(league_name, "通用")
