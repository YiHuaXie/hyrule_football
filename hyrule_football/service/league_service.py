from hyrule_football.repositories.league_repo import LeagueRepo
from hyrule_football.database import db_session, Session
from hyrule_football.service import oh_service as oh
from hyrule_football.service import dqd_service as dqd
from hyrule_football.utils import get_logger, match_league_name

logger = get_logger(__name__)


def _sync_oh_league_data(db: Session) -> int:
    league_list = oh.request_league_data()
    if not league_list:
        return 0

    count = 0

    for league_data in league_list:
        try:
            league_id = league_data.get("leagueId")
            league_name = league_data.get("leagueName")
            is_cup = league_data.get("isCup")

            if not league_id or not league_name:
                logger.debug(f"⚠️ 跳过无效数据：{league_data}")
                continue

            LeagueRepo.create(db, name=league_name, oh_id=league_id, is_cup=is_cup)
            count += 1
        except Exception as e:
            logger.error(f"❌ 导入欧核联赛失败 {league_data}: {e}")
            continue

    return count


def _sync_dqd_league_data(db: Session) -> int:
    data = dqd.request_league_data()
    if not data:
        return 0

    count = 0

    for league_data in data:
        try:
            league_id = league_data.get("competition_id")
            league_name = league_data.get("label")
            if not league_id or not league_name:
                logger.debug(f"⚠️ 跳过无效数据：{league_data}")
                continue

            standard_name = match_league_name(league_name)
            if not standard_name:
                logger.debug(f"⚠️ 无法匹配联赛: {league_name} (ID: {league_id})")
                continue

            logger.debug(f"✅ 匹配成功: {league_name} → {standard_name}")

            main_league = LeagueRepo.get_by_name(db, name=standard_name)
            if not main_league:
                logger.debug(f"⚠️ 主表中未找到联赛: {standard_name} (原名: {league_name})")
                continue

            LeagueRepo.update_dqd_id(db, main_league.id, league_id)
            count += 1
        except Exception as e:
            logger.error(f"❌ 导入懂球帝联赛失败 {league_data}: {e}")
            continue

    return count


def sync_league_data():
    with db_session() as db:
        try:
            oh_count = _sync_oh_league_data(db)
            logger.info(f"✅ 欧核联赛同步完成，共 {oh_count} 条")

            dqd_count = _sync_dqd_league_data(db)
            logger.info(f"✅ 懂球帝联赛同步完成，共 {dqd_count} 条")

            # 统一提交事务
            db.commit()
            logger.info("🎉 联赛数据同步完成！")

        except Exception as e:
            logger.error(f"❌ 同步联赛数据失败：{e}")
            db.rollback()
            raise
