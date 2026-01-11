from hyrule_football.service.team_sync_service import TeamSyncService
from hyrule_football.repositories.league_repo import LeagueRepo
from hyrule_football.schemas import SeasonSchema
from hyrule_football.models import League
from hyrule_football.database import db_async_session
from hyrule_football.utils import get_logger, specific_season_name
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import sys
import asyncio
import inspect

logger = get_logger(__name__)


async def _sync_teams_from_seasons(db: AsyncSession, league_name: str, seasons: List[str]):
    """同步指定联赛指定赛季下的球队"""
    if not seasons:
        logger.info(f"❌ {league_name} has no input season data, skip")
        return

    league = await LeagueRepo(db).get_by_name(league_name)
    # 1. 判断 league 是否可以同步球队
    if not league:
        logger.info(f"❌ {league_name} not found, skip")
        return

    if league.is_cup == 1:
        logger.info(f"❌ {league_name} is cup, skip")
        return

    if not league.oh_seasons:
        logger.info(f"❌ {league_name} has no OH seasons, skip")
        return

    # 2. 标准化 seasons
    matched_seasons = []
    for season in seasons:
        season_name = specific_season_name(league_name, season)
        oh_season = next((s for s in league.oh_seasons if s.get("name") == season_name), None)
        if oh_season:
            matched_seasons.append(oh_season.get("name"))

    if not matched_seasons:
        logger.info(f"❌ {league_name} has no matched season data, skip")
        return

    print(f"{"=" * 50}")
    print(f"{league.name} matched seasons: {matched_seasons}")
    # 3. 同步球队
    for season in matched_seasons:
        logger.info(f"🚀 sync teams from {league.name}-{season}...")
        service = TeamSyncService(db)
        teams = await service.sync_teams_from_season(league, season)
        await db.commit()
        logger.info(f"✅ {league.name}-{season} synced {len(teams)} teams")

    print(f"{"=" * 50}")


def _oh_current_season_by_league(league: League) -> Optional[str]:
    if league and league.oh_season:
        return league.oh_season.get("name")

    if league and league.oh_seasons:
        return league.oh_seasons[0].get("name")

    return None


def _oh_seasons_by_league(league: League) -> List[str]:
    if league and league.oh_seasons:
        return [s.get("name") for s in league.oh_seasons if s.get("name")]

    return []


async def _get_leagues_by_names(db: AsyncSession, league_names: List[str]):
    repo = LeagueRepo(db)
    result = []
    for league_name in league_names:
        league = await repo.get_by_name(league_name)
        if league:
            result.append(league)

    if not result:
        result = await repo.get_leagues_with_both()
    return result


async def sync_teams_from_leagues_current_season(*league_names: str):
    """同步指定联赛当前赛季下的球队"""
    async with db_async_session() as db:
        leagues = await _get_leagues_by_names(db, list(league_names))
        for league in leagues:
            current_season = _oh_current_season_by_league(league)
            season_list = [current_season] if current_season else []
            await _sync_teams_from_seasons(db, league.name, season_list)


async def sync_teams_from_leagues_all_seasons(*league_names: str):
    """同步指定联赛所有赛季下的球队"""
    async with db_async_session() as db:
        leagues = await _get_leagues_by_names(db, list(league_names))
        for league in leagues:
            season_list = _oh_seasons_by_league(league)
            await _sync_teams_from_seasons(db, league.name, season_list)


async def sync_teams_from_season(league_name: str, season: Optional[str] = None):
    """同步联赛赛季下的球队, season 为空时同步当前赛季"""
    async with db_async_session() as db:
        season_list = []
        if not season:
            league = await LeagueRepo(db).get_by_name(league_name)
            current_season = _oh_current_season_by_league(league)
            if current_season:
                season_list.append(current_season)
        else:
            season_list.append(season)

        await _sync_teams_from_seasons(db, league_name, season_list)


async def sync_teams_from_seasons(league_name: str, *seasons: str):
    """同步指定联赛指定赛季下的球队, seasons 为空同步所有赛季"""
    async with db_async_session() as db:
        season_list = list(seasons)
        if not season_list:
            league = await LeagueRepo(db).get_by_name(league_name)
            season_list = _oh_seasons_by_league(league)

        await _sync_teams_from_seasons(db, league_name, season_list)


TASKS = {
    "sync_teams_from_season": sync_teams_from_season,
    "sync_teams_from_seasons": sync_teams_from_seasons,
    "sync_teams_from_leagues_current_season": sync_teams_from_leagues_current_season,
    "sync_teams_from_leagues_all_seasons": sync_teams_from_leagues_all_seasons,
}


# =====================
# CLI 入口
# =====================
def main():
    if len(sys.argv) < 2:
        print("用法: python team_sync.py <task> [args...]")
        print(f"可用任务: {', '.join(TASKS.keys())}")
        sys.exit(1)

    task_name = sys.argv[1]
    task = TASKS.get(task_name)

    if not task:
        print(f"❌ 未知任务: {task_name}")
        print(f"可用任务: {', '.join(TASKS.keys())}")
        sys.exit(1)

    args = sys.argv[2:]

    if inspect.iscoroutinefunction(task):
        asyncio.run(task(*args))
    else:
        task(*args)


if __name__ == "__main__":
    main()
