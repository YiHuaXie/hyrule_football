from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from hyrule_football.schemas import MatchBase, MatchBase, MatchMatcher, DQDMatch
from hyrule_football.store import daily_match_store
from hyrule_football.utils import get_logger, LEAGUE_ALIASES
from hyrule_football.service import dqd_service as dqd
from hyrule_football.service import oh_service as oh
from hyrule_football.database import db_async_session
from hyrule_football.repositories.match_repo import MatchRepo
from hyrule_football.repositories.team_repo import TeamRepo
from hyrule_football.repositories.league_repo import LeagueRepo

logger = get_logger(__name__)


def get_match_for_name(match_name: str) -> List[MatchBase]:
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
) -> MatchBase | List[MatchBase] | None:
    team_a = team_a.strip()
    if not team_a:
        return None

    team_b = team_b.strip() if team_b else None

    matches = get_daily_match_list()
    # 情况 1：双队匹配 → 返回单个 MatchBase 或 None
    if team_b:
        for m in matches:
            desc = m.match_description
            if team_a in desc and team_b in desc:
                return m
        return None  # 没找到双队匹配时返回 None

    # 情况 2：单队匹配 → 返回 List[MatchBase]
    result_list: List[MatchBase] = []
    for m in matches:
        if team_a in m.match_description:
            result_list.append(m)

    return result_list


def get_daily_match_list() -> List[MatchBase]:
    matches = daily_match_store.list_matches()
    return matches


async def sync_daily_match_list() -> List[MatchBase]:
    try:
        dqd_match_list = dqd.request_daily_match_list()
        # print(dqd_match_list[0])
        dqd_match_list = [DQDMatch(**m) for m in dqd_match_list]

        match_list = oh.request_daily_match_list()
        # print(match_list[0])
        valid_match_list = []
        async with db_async_session() as db:
            # 1. 过滤掉联赛不存在的比赛
            for match_data in match_list:
                match_base = MatchBase(**match_data)
                db_league = await LeagueRepo.get_by_oh_id(db, match_base.oh_league_id)
                if not db_league:
                    continue
                valid_match_list.append(match_base)

            # # 2. 合并懂球帝数据并保存到数据库
            # for vm in valid_match_list:
            #     matcher = MatchMatcher(vm)
            #     same_league_match_list = [
            #         dqd_m
            #         for dqd_m in dqd_match_list
            #         if dqd_m.competition_name in LEAGUE_ALIASES.get(vm.league, [])
            #     ]
            #     # 合并懂球帝数据
            #     for dqd_m in same_league_match_list:
            #         if matcher.merge_dqd_match(dqd_m):
            #             break

            #     # 保存到数据库
            #     await sync_match_and_team_to_db(db, vm)

        # 3.将有效赛事保存到 redis
        daily_match_store.save_matches(valid_match_list)

        logger.info(f"✅ 已同步 {len(valid_match_list)} 场赛事")
        return valid_match_list

    except Exception as e:
        logger.error(f"❌ 同步赛事列表失败：{e}")
        return []


async def sync_match_and_team_to_db(db: AsyncSession, match: MatchBase):
    """同步比赛和球队到数据库"""
    db_league = await LeagueRepo.get_by_oh_id(db, match.oh_league_id)
    if not db_league:
        return

    db_home_team = await TeamRepo.create_or_update(
        db,
        match.home,
        oh_id=match.oh_home_team_id,
        dqd_id=match.dqd_home_team_id,
    )

    db_away_team = await TeamRepo.create_or_update(
        db,
        match.away,
        oh_id=match.oh_away_team_id,
        dqd_id=match.dqd_away_team_id,
    )

    match_dict = match.to_db_dict(db_league.id, db_home_team.id, db_away_team.id)
    await MatchRepo.create_or_update(db, oh_match_id=match.oh_match_id, **match_dict)
