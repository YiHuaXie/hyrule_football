from dotenv import load_dotenv
from pathlib import Path


load_dotenv()

from hyrule_football.clients.lark_client import start_lark_client
from hyrule_football.utils import configure_root_logger
from hyrule_football.config import settings


def main():
    log_level = settings.LOG_LEVEL.upper()
    log_file = Path("logs") / settings.LOG_FILE
    configure_root_logger(level=log_level, log_file=log_file)
    start_lark_client()


if __name__ == "__main__":
    main()
