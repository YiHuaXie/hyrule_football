from pathlib import Path
from hyrule_football.clients.lark_client import start_lark_client
from hyrule_football.utils import configure_root_logger
from hyrule_football.config import settings
from hyrule_football.tasks import match_task


def main():
    log_level = settings.LOG_LEVEL.upper()
    log_file = Path("logs") / settings.LOG_FILE
    configure_root_logger(level=log_level, log_file=log_file)

    match_task.start_scheduler()

    start_lark_client()


if __name__ == "__main__":
    main()
