from typing import List
from mcp.server.fastmcp import FastMCP
from hyrule_football.schema.company import fixed_company_list
from hyrule_football.store import daily_match_store
from hyrule_football.service.odds_service import get_odds_for_match
from hyrule_football.utils import get_logger

logger = get_logger(__name__)

odds_mcp = FastMCP("Odds")
# 设置 MCP 端点路径为根路径（实际路径由 Starlette Mount 控制）
odds_mcp.settings.streamable_http_path = "/"


@odds_mcp.tool(description="查询某场比赛的赔率数据")
def get_odds_detail_for_match(
    match_id: str,
    company_names: List[str] = ["bet365", "威廉希尔"],
) -> dict:
    logger.info(f">>> [Tool] get_odds_info_for_match 被调用，入参：{match_id}, {company_names}")
    match_info = daily_match_store.get_match(match_id)
    if not match_info:
        return {}

    company_list = fixed_company_list(company_names)
    odds_info = get_odds_for_match(match_info, company_list)
    return odds_info.model_dump()


if __name__ == "__main__":
    odds_mcp.run(transport="streamable-http")
