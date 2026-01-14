from hyrule_football.utils.deep_get import deep_get

SEASON_MAP = {
    "欧洲杯": {
        "2023-2024": "2024",
        "2019-2021": "2020",
    }
}


def _is_int(value: str) -> bool:
    try:
        int(value)
        return True
    except ValueError:
        return False


def standard_year(year: int) -> int:
    year = int(year)

    if year < 50:
        return year + 2000
    elif year < 100:
        return year + 1900
    return year


def specific_season_name(league_name: str, season_name: str) -> str:
    """标准化赛季名称"""
    if not season_name:
        return ""

    if league_name in SEASON_MAP.keys():
        season_name = deep_get(SEASON_MAP, [league_name, season_name], season_name)

    season_name = season_name.replace("/", "-")
    years = season_name.split("-")
    if len(years) == 1:
        return str(standard_year(years[0])) if _is_int(years[0]) else ""

    start, end = years[:2]
    if _is_int(start) and _is_int(end):
        return f"{standard_year(start)}-{standard_year(end)}"

    return ""


def season_sort_key(season_name: str) -> int:
    if not season_name:
        return -1

    years = season_name.replace("/", "-").split("-")
    if len(years) == 1:
        return standard_year(years[0]) if _is_int(years[0]) else -1

    start, end = years[:2]
    return standard_year(start) if _is_int(start) else -1
