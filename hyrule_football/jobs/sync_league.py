from hyrule_football.service.league_sync_service import LeagueSyncService
from hyrule_football.repositories.league_repo import LeagueRepo
from hyrule_football.database import db_async_session
from hyrule_football.utils import get_logger
import sys
import asyncio
import inspect

logger = get_logger(__name__)


# ========
# 联赛同步
# ========
async def sync_leagues():
    logger.info("🚀 sync leagues...")
    service = LeagueSyncService.create()
    result = await service.sync_leagues()
    for platform, leagues in result.items():
        logger.info(f"✅ {platform.value} leagues synced, count: {len(leagues)}")
    logger.info("✅ leagues synced")


# ========
# 赛季同步
# ========
async def sync_seasons_by_leagues(*names: str):
    """同步指定联赛的赛季数据，names 为空时同步所有联赛"""
    names = list(names)
    leagues = []
    async with db_async_session() as db:
        repo = LeagueRepo(db)
        if not names:
            leagues = [(l.id, l.name) for l in await repo.get_leagues_with_both()]
        else:
            leagues = [(l.id, l.name) for l in await repo.get_leagues_by_names(names)]

    service = LeagueSyncService.create()
    for league_id, league_name in leagues:
        logger.info(f"🚀 sync {league_name} league seasons...")
        result = await service.sync_seasons_by_league(league_id)
        for platform, success in result.items():
            logger.info(f" {platform.value} sync {league_name} league seasons {"success" if success else "failed"}")
        logger.info(f"✅ {league_name} league seasons synced")


TASKS = {
    "sync_leagues": sync_leagues,
    "sync_seasons_by_leagues": sync_seasons_by_leagues,
}


# =====================
# CLI 入口
# =====================
def main():
    if len(sys.argv) < 2:
        print("用法: python sync_league.py <task> [args...]")
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
