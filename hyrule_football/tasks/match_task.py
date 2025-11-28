from apscheduler.schedulers.background import BackgroundScheduler
from hyrule_football.service.match_service import sync_daily_match_list
from hyrule_football.utils import get_logger
import time

logger = get_logger(__name__)


def start_scheduler() -> None:
    """启动定时任务调度器"""
    scheduler = BackgroundScheduler(timezone="Asia/Shanghai")

    scheduler.add_job(
        sync_daily_match_list,
        "cron",
        hour="0,3,6,9,12,15,18,21",
        minute=0,
    )

    scheduler.start()


if __name__ == "__main__":
    start_scheduler()

    try:
        while True:
            time.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        pass
