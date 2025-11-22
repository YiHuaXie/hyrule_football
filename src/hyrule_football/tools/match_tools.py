from hyrule_football.core import match_service as _match_service
from langchain.tools import tool
from hyrule_football.utils import get_logger
from hyrule_football.models import MatchInfo
from typing import Optional, List
from pydantic import BaseModel, Field
from typing_extensions import Annotated
from hyrule_football.store import get_match_store

logger = get_logger(__name__)


@tool
def update_match_list() -> List[str]:
    """更新赛事列表"""
    logger.info(">>> [Tool] update_match_list 被调用")
    matches = _match_service.request_all_match_list()
    match_list = [m.match_description for m in matches]
    return match_list


@tool
def get_match_list() -> List[str]:
    """查询所有比赛（赛事）"""

    logger.info(">>> [Tool] get_match_list 被调用")
    matches = get_match_store().list_matches()
    match_list = [m.match_description for m in matches]
    return match_list


class MatchInput(BaseModel):
    """生成赛事对阵输入模型"""

    team_a: Annotated[str, Field(..., description="球队A")]
    team_b: Annotated[str, Field(..., description="球队B")]

    @property
    def matchup_str(self) -> str:
        """生成赛事对阵"""
        return f"{self.team_a} VS {self.team_b}"


@tool(parse_docstring=True)
def get_match_for_matchup(input_value: MatchInput) -> Optional[MatchInfo]:
    """
    查询某场比赛的赛事数据

    Args:
        input_value (MatchInput): 赛事对阵输入,
        传入 MatchInput，则使用其中的 team_a 与 team_b 生成赛事名称。
        例如 MatchInput(team_a="阿森纳", team_b="切尔西")，相当于 “阿森纳 VS 切尔西”

    Returns:
        Optional[MatchInfo]: 匹配到的赛事信息
    """

    logger.info(f">>> [Tool] get_match_for_matchup 被调用，入参：{input_value}")

    input_value = input_value.matchup_str
    matches = _match_service.get_match_for_name(input_value)
    if not matches:
        return None
    return matches[0]


@tool(parse_docstring=True)
def get_match_for_team(team_name: str) -> List[str]:
    """
    查询某只球队的赛事信息

    Args:
        team_name (str): 赛事信息摘要
        例如“皇马” 或 “拜仁”；

    Returns:
        List[str]: 匹配到的赛事信息
    """

    logger.info(f">>> [Tool] get_match_for_team 被调用，入参：{team_name}")

    matches = _match_service.get_match_for_name(team_name)
    return [m.match_description for m in matches]
