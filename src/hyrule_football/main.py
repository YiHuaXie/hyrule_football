from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

from hyrule_football.clients.lark_client import start_lark_client
from hyrule_football.utils import configure_root_logger
import os


def main():
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_file = Path("logs") / os.getenv("LOG_FILE", "app.log")
    configure_root_logger(level=log_level, log_file=log_file)
    start_lark_client()


if __name__ == "__main__":
    main()
