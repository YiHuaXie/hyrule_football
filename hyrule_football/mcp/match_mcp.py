from pathlib import Path
from typing import List

from mcp.server.fastmcp import FastMCP

from hyrule_football.config import settings
from hyrule_football.schema import MatchInfo
from hyrule_football.service import match_service
from hyrule_football.utils import configure_root_logger, get_logger

# 确保 MCP 子进程也把日志写入同一个日志文件
configure_root_logger(log_file=Path("logs") / settings.LOG_FILE)
logger = get_logger(__name__)

match_mcp = FastMCP("Match")


@match_mcp.tool(description="查询所有比赛")
def get_match_list() -> List[dict]:
    logger.info(">>> [Tool] get_match_list 被调用")
    matches = match_service.get_daily_match_list()
    return [m.model_dump() for m in matches]


@match_mcp.tool(description="根据球队名查询某支球队的比赛数据")
def get_match_for_team(team_name: str) -> List[dict]:
    logger.info(f">>> [Tool] get_match_for_team 被调用，入参：{team_name}")
    matches = match_service.get_fixed_daily_matches(team_name)
    if not matches:
        return []
    return [m.model_dump() for m in matches]


@match_mcp.tool(
    description="根据球队对阵查询某场比赛的比赛数据。team_a 与 team_b 均为必填，返回匹配的对阵比赛数据。"
)
def get_match_for_matchup(team_a: str, team_b: str) -> dict:
    logger.info(f">>> [Tool] get_match_for_matchup 被调用，入参：{team_a} VS {team_b}")
    result = match_service.get_fixed_daily_matches(team_a, team_b)
    if isinstance(result, list):
        return result[0].model_dump()
    if isinstance(result, MatchInfo):
        return result.model_dump()

    return {}


if __name__ == "__main__":
    match_mcp.run(transport="stdio")
