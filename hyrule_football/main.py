from pathlib import Path
from hyrule_football.clients.lark_client import start_lark_client_thread
from hyrule_football.utils import configure_root_logger
from hyrule_football.config import settings
from hyrule_football.tasks import match_task
import time


def main():
    log_level = settings.LOG_LEVEL.upper()
    log_file = Path("logs") / settings.LOG_FILE
    configure_root_logger(level=log_level, log_file=log_file)
    # 启动定时任务
    match_task.start_scheduler()
    # 启动飞书客户端
    start_lark_client_thread()

    try:
        while True:
            time.sleep(300)
            print("主程序保活中，所有服务正常运行")
    except KeyboardInterrupt:
        print("收到退出信号，程序正常关闭")


if __name__ == "__main__":
    main()
