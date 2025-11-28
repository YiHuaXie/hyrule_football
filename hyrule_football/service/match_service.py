from typing import List
from hyrule_football.schema import MatchInfo
from hyrule_football.store import daily_match_store
from hyrule_football.utils import get_logger

from .api_service import request_hot_match_list
from .api_service import request_daily_match_list

logger = get_logger(__name__)


def get_match_for_name(match_name: str) -> List[MatchInfo]:
    team_list = match_name.upper().split("VS")
    if len(team_list) == 2:
        team_a = team_list[0].strip()
        team_b = team_list[1].strip()
    else:
        team_a = None
        team_b = None

    matches = daily_match_store.list_matches()
    if not matches:
        matches = sync_daily_match_list()

    match_list = []
    for a_match in matches:
        match_desc = a_match.match_description
        condition_1 = team_a and team_b and (team_a in match_desc and team_b in match_desc)
        condition_2 = match_name in match_desc
        if condition_1 or condition_2:
            match_list.append(a_match)

    return match_list


def get_hot_match_list() -> List[MatchInfo]:
    return [MatchInfo(**m) for m in request_hot_match_list()]


def sync_daily_match_list() -> List[MatchInfo]:
    try:
        match_list = request_daily_match_list()
        matches = [MatchInfo(**m) for m in match_list]
        daily_match_store.save_matches(matches)
        logger.info(f"✅ 已同步 {len(matches)} 场赛事")
        return matches
    except Exception as e:
        logger.error(f"❌ 同步赛事列表失败：{e}")
        return []
