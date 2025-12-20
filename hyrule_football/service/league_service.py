from hyrule_football.repositories.league_repo import LeagueRepo
from hyrule_football.database import db_async_session
from hyrule_football.service import oh_service as oh
from hyrule_football.service import dqd_service as dqd
from hyrule_football.utils import get_logger, match_league_name
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(__name__)


async def _sync_oh_league_data(db: AsyncSession) -> int:
    league_list = oh.request_league_data()
    count = 0
    for league_data in league_list:
        try:
            league_id = league_data.get("leagueId")
            league_name = league_data.get("leagueName")
            is_cup = league_data.get("cup", 0)

            if not league_id or not league_name:
                continue

            await LeagueRepo.create_or_update(
                db,
                name=league_name,
                oh_id=league_id,
                is_cup=is_cup,
            )
            count += 1
        except Exception as e:
            logger.error(f"❌ 导入欧核联赛失败 {league_data}: {e}")
            continue

    return count


async def _sync_dqd_league_data(db: AsyncSession) -> int:
    data = dqd.request_league_data()
    count = 0
    for league_data in data:
        try:
            league_id = league_data.get("competition_id")
            league_name = league_data.get("label")
            if not league_id or not league_name:
                continue

            standard_name = match_league_name(league_name)
            if not standard_name:
                continue

            db_league = await LeagueRepo.get_by_name(db, name=standard_name)
            if not db_league:
                continue

            await LeagueRepo.update(db, db_league.id, dqd_id=league_id)
            count += 1
        except Exception as e:
            logger.error(f"❌ 导入懂球帝联赛失败 {league_data}: {e}")
            continue

    return count


async def sync_league_data():
    try:
        async with db_async_session() as db:
            oh_count = await _sync_oh_league_data(db)
            logger.info(f"✅ 欧核联赛同步完成，共 {oh_count} 条")

            dqd_count = await _sync_dqd_league_data(db)
            logger.info(f"✅ 懂球帝联赛同步完成，共 {dqd_count} 条")
    except Exception as e:
        logger.error(f"❌ 同步联赛数据失败：{e}")
