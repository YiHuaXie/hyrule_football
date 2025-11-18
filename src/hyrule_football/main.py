from dotenv import load_dotenv

load_dotenv()

from hyrule_football.clients.lark_client import start_lark_client
from hyrule_football.utils import configure_root_logger


def main():
    configure_root_logger()
    start_lark_client()


if __name__ == "__main__":
    main()
