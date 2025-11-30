from apscheduler.schedulers.background import BackgroundScheduler
from hyrule_football.service.match_service import sync_daily_match_list
from hyrule_football.utils import get_logger

logger = get_logger(__name__)


def _daily_match_scheduler() -> None:
    """定时同步每日比赛数据"""
    logger.info("✅启动每日赛事同步任务")
    scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
    scheduler.add_job(
        sync_daily_match_list,
        "cron",
        hour="0,3,6,9,12,15,18,21",
        minute=0,
    )
    scheduler.start()


def start_scheduler() -> None:
    _daily_match_scheduler()
