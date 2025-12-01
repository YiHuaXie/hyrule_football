from apscheduler.schedulers.background import BackgroundScheduler
from hyrule_football.service.match_service import sync_daily_match_list
from hyrule_football.utils import get_logger

logger = get_logger(__name__)


def daily_match_task() -> None:
    """定时同步每日比赛数据"""
    logger.info("✅启动每日赛事同步任务")
    scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
    # 每 3 小时同步一次
    scheduler.add_job(sync_daily_match_list, "interval", hours=3)
    scheduler.start()
