from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from hyrule_football.schemas import MatchBase
from hyrule_football.store import daily_match_store
from hyrule_football.utils import get_logger
from hyrule_football.service import dqd_service as dqd
from hyrule_football.service import oh_service as oh
from hyrule_football.database import db_async_session
from hyrule_football.repositories.match_repo import MatchRepo
from hyrule_football.repositories.team_repo import TeamRepo
from hyrule_football.repositories.league_repo import LeagueRepo
from hyrule_football.config import settings
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from .match_zip_engine import MatchZipEngine

logger = get_logger(__name__)


async def sync_daily_match_list() -> List[MatchBase]:
    try:
        async with db_async_session() as db:
            leagues = await LeagueRepo.get_all(db)
            engine = MatchZipEngine(db, leagues)

            dqd_matches = dqd.request_daily_match_list()
            dqd_matches_map = engine.dqd_matches_map(dqd_matches)

            oh_matches = oh.request_match_list(engine.oh_league_ids)
            oh_matches = engine.oh_matches(oh_matches)

            matches = await engine.matches_zip(oh_matches, dqd_matches_map)

        daily_match_store.save_matches(matches)

        logger.info(f"✅ 已同步 {len(matches)} 场赛事")

        return matches
    except Exception as e:
        logger.error(f"❌ 同步每日赛事失败：{e}")
        return []


async def sync_daily_played_match_list():
    """同步已完赛数据到数据库"""

    date_now = datetime.now(ZoneInfo(settings.TZ))
    today_start = date_now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_start_str = today_start.strftime("%Y-%m-%d %H:%M:%S")
    yesterday_start = today_start - timedelta(days=1)
    yesterday_start_str = yesterday_start.strftime("%Y-%m-%d %H:%M:%S")
    two_days_ago_start = yesterday_start - timedelta(days=1)
    two_days_ago_start_str = two_days_ago_start.strftime("%Y-%m-%d %H:%M:%S")
    three_days_ago_start = two_days_ago_start - timedelta(days=1)
    three_days_ago_start_str = three_days_ago_start.strftime("%Y-%m-%d %H:%M:%S")
    four_days_ago_start = three_days_ago_start - timedelta(days=1)
    four_days_ago_start_str = four_days_ago_start.strftime("%Y-%m-%d %H:%M:%S")
    five_days_ago_start = four_days_ago_start - timedelta(days=1)
    five_days_ago_start_str = five_days_ago_start.strftime("%Y-%m-%d %H:%M:%S")

    try:
        async with db_async_session() as db:
            leagues = await LeagueRepo.get_all(db)
            engine = MatchZipEngine(db, leagues)

            dqd_matches = []
            for date_start in [
                five_days_ago_start_str,
                four_days_ago_start_str,
                three_days_ago_start_str,
                two_days_ago_start_str,
                yesterday_start_str,
                today_start_str,
            ]:
                tmp_matches = dqd.request_played_match_list(date_start)
                dqd_matches.extend(tmp_matches)

            dqd_matches_map = engine.dqd_matches_map(dqd_matches)

            oh_matches = oh.request_match_list(engine.oh_league_ids, type=2)
            oh_matches = engine.oh_matches(oh_matches)

            matches = await engine.matches_zip(oh_matches, dqd_matches_map)
            tmp_matches = [
                m for m in matches if m.oh_home_team_id == 1376 or m.oh_away_team_id == 1376
            ]
            for m in matches:
                await _sync_match_to_db(db, m)

        logger.info(f"✅ 已同步 {len(matches)} 场已完赛赛事")
        return matches
    except Exception as e:
        logger.error(f"❌ 同步已完赛赛事列表失败：{e}")
        return []

async def sync_matches_by_league_round(league_id: int, season: str, round: str):
    pass

async def _sync_match_to_db(db: AsyncSession, match: MatchBase):
    """同步比赛和球队到数据库"""
    league = await LeagueRepo.get_by_oh_id(db, match.oh_league_id)
    if not league:
        return

    team_repo = TeamRepo(db)
    home_team = await team_repo.create_or_update(
        match.home,
        match.oh_home_team_id,
        match.dqd_home_team_id,
    )

    away_team = await team_repo.create_or_update(
        match.away,
        match.oh_away_team_id,
        match.dqd_away_team_id,
    )

    match_dict = match.to_db_dict(league.id, home_team.id, away_team.id)
    await MatchRepo.create_or_update(db, match.oh_match_id, **match_dict)
