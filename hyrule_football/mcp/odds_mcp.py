from pathlib import Path
from typing import List

from mcp.server.fastmcp import FastMCP

from hyrule_football.config import settings
from hyrule_football.schema import Company
from hyrule_football.store import daily_match_store
from hyrule_football.service.odds_service import get_odds_for_match
from hyrule_football.utils import configure_root_logger, get_logger

configure_root_logger(log_file=Path("logs") / settings.LOG_FILE)
logger = get_logger(__name__)

odds_mcp = FastMCP("Odds")


@odds_mcp.tool(description="查询某场比赛的赔率数据")
def get_odds_detail_for_match(
    match_id: str,
    company_list: List[str] = ["bet365", "威廉希尔"],
) -> dict:
    logger.info(">>> [Tool] get_odds_info_for_match 被调用")
    match_info = daily_match_store.get_match(match_id)
    if not match_info:
        return {}

    company_list = [c for name in company_list if (c := Company.from_name(name))] or [
        Company.bet635(),
        Company.williamhill(),
    ]

    odds_info = get_odds_for_match(match_info, company_list)
    return odds_info.model_dump()


if __name__ == "__main__":
    odds_mcp.run(transport="stdio")
