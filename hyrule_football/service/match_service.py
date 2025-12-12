from typing import List, Optional
from hyrule_football.schema import MatchInfo, MatchModel, MatchMatcher, DQDMatchModel
from hyrule_football.store import daily_match_store
from hyrule_football.utils import get_logger, LEAGUE_ALIASES

from .api_service import request_hot_match_list
from .api_service import request_daily_match_list

from hyrule_football.service import dqd_service as dqd
from hyrule_football.service import oh_service as oh
from hyrule_football.database import db_session, Session
from hyrule_football.repositories.league_repo import LeagueRepo

logger = get_logger(__name__)


def get_match_for_name(match_name: str) -> List[MatchInfo]:
    team_list = match_name.upper().split("VS")
    if len(team_list) == 2:
        team_a = team_list[0].strip()
        team_b = team_list[1].strip()
    else:
        team_a = None
        team_b = None

    matches = get_daily_match_list()

    match_list = []
    for a_match in matches:
        match_desc = a_match.match_description
        condition_1 = team_a and team_b and (team_a in match_desc and team_b in match_desc)
        condition_2 = match_name in match_desc
        if condition_1 or condition_2:
            match_list.append(a_match)

    return match_list


def get_fixed_daily_matches(
    team_a: str,
    team_b: Optional[str] = None,
) -> MatchInfo | List[MatchInfo] | None:
    team_a = team_a.strip()
    if not team_a:
        return None

    team_b = team_b.strip() if team_b else None

    matches = get_daily_match_list()
    # 情况 1：双队匹配 → 返回单个 MatchInfo 或 None
    if team_b:
        for m in matches:
            desc = m.match_description
            if team_a in desc and team_b in desc:
                return m
        return None  # 没找到双队匹配时返回 None

    # 情况 2：单队匹配 → 返回 List[MatchInfo]
    result_list: List[MatchInfo] = []
    for m in matches:
        if team_a in m.match_description:
            result_list.append(m)

    return result_list


def get_hot_match_list() -> List[MatchInfo]:
    return [MatchInfo(**m) for m in request_hot_match_list()]


def get_daily_match_list() -> List[MatchInfo]:
    matches = daily_match_store.list_matches()
    if not matches:
        matches = sync_daily_match_list()
    return matches


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


def new_sync_daily_match_list() -> List[MatchModel]:
    try:

        oh_match_list = oh.request_daily_match_list()
        oh_match_list = [MatchModel(**m) for m in oh_match_list]
        dqd_match_list = dqd.request_app_daily_match_list()
        dqd_match_list = [DQDMatchModel(**m) for m in dqd_match_list]
        for oh_m in oh_match_list:
            print(oh_m.match_description)
            matcher = MatchMatcher(oh_m)
            same_league_match_list = [
                m
                for m in dqd_match_list
                if m.competition_name in LEAGUE_ALIASES.get(oh_m.league, [])
            ]

            for dqd_m in same_league_match_list:
                if matcher.merge_dqd_match(dqd_m):
                    break

        return oh_match_list
    except Exception as e:
        logger.error(f"❌ 同步赛事列表失败：{e}")
        return []
