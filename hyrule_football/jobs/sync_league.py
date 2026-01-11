from hyrule_football.service.league_sync_service import OHLeagueSyncService, DQDLeagueSyncService
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
    async with db_async_session() as db:
        logger.info("🚀 sync OH leagues...")
        leagues = await OHLeagueSyncService(db).sync_leagues()
        logger.info(f"✅ OH leagues synced, count: {len(leagues)}")

        logger.info("🚀 sync DQD leagues...")
        leagues = await DQDLeagueSyncService(db).sync_leagues()
        logger.info(f"✅ DQD leagues synced, count: {len(leagues)}")


# ========
# 赛季同步
# ========
async def sync_seasons_by_leagues(*names: str):
    """同步指定联赛的赛季数据，names 为空时同步所有联赛"""
    logger.info("🚀 sync league seasons...")

    names = list(names)
    async with db_async_session() as db:
        repo = LeagueRepo(db)
        matched_leagues = []
        if not names:
            matched_leagues = await repo.get_leagues_with_both()
        else:
            matched_leagues = await repo.get_leagues_by_names(names)

        for league in matched_leagues:
            logger.info(f"🚀 sync {league.name} league seasons...")
            result = await OHLeagueSyncService(db).sync_league_seasons(league)
            if not result:
                logger.info(f"❌ {league.name} sync oh league seasons failed")

            result = await DQDLeagueSyncService(db).sync_league_seasons(league)
            if not result:
                logger.info(f"❌ {league.name} sync dqd league seasons failed")

            logger.info(f"✅ {league.name} league seasons synced")


TASKS = {
    "sync_leagues": sync_leagues,
    "sync_seasons_by_leagues": sync_league_seasons_by_names,
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
