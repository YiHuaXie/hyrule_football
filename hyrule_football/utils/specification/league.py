import json
from pathlib import Path
from typing import Optional, Dict, List


# ========== 加载别名映射表 ==========
def load_league_aliases() -> Dict[str, List[str]]:
    current_file = Path(__file__)
    hyrule_root = current_file.parent.parent
    json_path = hyrule_root / "data" / "league_aliases.json"

    if not json_path.exists():
        return {}

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {}


# 全局加载别名映射表
LEAGUE_ALIASES = load_league_aliases()


def specific_league_name(target_name: str) -> Optional[str]:
    """从别名映射表中匹配标准联赛名称，如果没有匹配到，说明是不支持的联赛，返回 None"""
    if not target_name:
        return None

    target_name = target_name.strip()

    for standard_name, aliases in LEAGUE_ALIASES.items():
        if target_name == standard_name:
            return standard_name

        if target_name in aliases:
            return standard_name

    return None
