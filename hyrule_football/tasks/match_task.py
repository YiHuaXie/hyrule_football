from apscheduler.schedulers.background import BackgroundScheduler
from hyrule_football.service.match_service import sync_daily_match_list
from hyrule_football.utils import get_logger
from hyrule_football.config import settings

logger = get_logger(__name__)


def daily_match_task() -> None:
    """定时同步每日比赛数据"""
    logger.info("✅启动每日赛事同步任务")
    scheduler = BackgroundScheduler(timezone=settings.TZ)
    # 每 3 小时执行一次
    scheduler.add_job(
        sync_daily_match_list,
        trigger="cron",
        hour="0-23/3",
        minute=0,
    )
    scheduler.start()
