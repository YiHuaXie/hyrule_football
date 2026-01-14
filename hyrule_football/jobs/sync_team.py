from hyrule_football.service.team_sync_service import TeamSyncService
from hyrule_football.repositories.league_repo import LeagueRepo
from hyrule_football.database import db_async_session
from hyrule_football.utils import get_logger
from typing import List
import sys
import asyncio
import inspect

logger = get_logger(__name__)


def get_season_names_by_oh(oh_seasons: List[dict]) -> List[str]:
    # 用倒序能提高球队关联的命中率
    # reversed
    return [s.get("name") for s in (oh_seasons or []) if s.get("name")]


async def get_leagues_by_names(league_names: List[str]):
    async with db_async_session() as db:
        repo = LeagueRepo(db)
        leagues = await repo.get_leagues_by_names(league_names)
        if not leagues:
            leagues = await repo.get_leagues_with_both()

        return [(l.name, l.oh_seasons) for l in leagues]


async def sync_teams_from_leagues_current_season(*league_names: str):
    """同步指定联赛当前赛季下的球队"""
    leagues = await get_leagues_by_names(list(league_names))
    service = TeamSyncService.create()
    for league_name, oh_seasons in leagues:
        current_season = oh_seasons[0].get("name") if oh_seasons else None
        logger.info(f"🚀 sync teams from {league_name}-{current_season}...")
        teams = await service.sync_teams_from_season(league_name, current_season)
        logger.info(f"✅ {league_name}-{current_season} synced, {len(teams)} teams")


async def sync_teams_from_leagues_all_seasons(*league_names: str):
    """同步指定联赛所有赛季下的球队"""
    leagues = await get_leagues_by_names(list(league_names))
    service = TeamSyncService.create()
    for league_name, oh_seasons in leagues:
        logger.info(f"🚀 sync teams from {league_name} all seasons...")
        season_names = get_season_names_by_oh(oh_seasons)
        for season_name in season_names:
            teams = await service.sync_teams_from_season(league_name, season_name)
            logger.info(f"✅ {league_name}-{season_name} synced, {len(teams)} teams")
        logger.info(f"✅ {league_name} all seasons synced")


async def sync_teams_from_seasons(league_name: str, *seasons: str):
    """同步指定联赛指定赛季下的球队, seasons 为空同步所有赛季"""
    async with db_async_session() as db:
        repo = LeagueRepo(db)
        league = await repo.get_by_name(league_name)
        if not league:
            logger.error(f"{league_name} not found")
            return

        league_name = league.name
        season_list = list(seasons)
        if not season_list:
            season_list = get_season_names_by_oh(league.oh_seasons)

    service = TeamSyncService.create()
    for season in season_list:
        logger.info(f"🚀 sync teams from {league_name}-{season}...")
        teams = await service.sync_teams_from_season(league_name, season)
        logger.info(f"✅ {league_name}-{season} synced, {len(teams)} teams")


TASKS = {
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
