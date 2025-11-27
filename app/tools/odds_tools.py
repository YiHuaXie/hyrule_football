from langchain.tools import tool
from app.utils import get_logger
from app.models import BasedMatchOddsInfo, get_company_by_name, MatchInfo, Company
from app.core.match_service import get_match_for_name
from app.core.odds_service import get_odds_for_match
from .match_tools import MatchInput
from typing import Optional, List
from pydantic import BaseModel, Field
from typing_extensions import Annotated

logger = get_logger(__name__)


class MatchOddsInput(MatchInput):
    """生成赛事赔率信息输入模型"""

    company_list: Annotated[
        List[str],
        Field(
            default_factory=lambda: ["365", "威廉"],  # 默认 bet365 和 威廉希尔
            description="博彩公司名字列表，默认为 bet365 和 威廉希尔",
        ),
    ]


class MatchOddsPlan(BaseModel):
    """已经解析好的赔率查询计划"""

    fix_match: Annotated[
        MatchInfo,
        Field(..., description="已经确认的比赛信息"),
    ]
    company_list: Annotated[
        List[Company],
        Field(..., description="需要查询的博彩公司名称列表"),
    ]


@tool(parse_docstring=True)
def plan_match_odds_query(match_input: MatchOddsInput) -> Optional[MatchOddsPlan]:
    """
    根据球队信息和可选的博彩公司列表，解析出唯一的一场比赛，并返回标准化后的赔率查询计划。

    Args:
        match_input (MatchOddsInput): 包含 team_a、team_b 和可选 company_list 的输入。

    Returns:
        Optional[MatchOddsPlan]: 若找到匹配比赛，则返回查询计划；否则返回 None。
    """

    logger.info(">>> [Tool] plan_match_odds_query 被调用")

    match_list = get_match_for_name(match_input.matchup_str)
    if not match_list:
        return None

    match_info = match_list[0]

    company_list = [
        company
        for company in (get_company_by_name(name) for name in match_input.company_list)
        if company is not None
    ]

    if not company_list:
        return None

    return MatchOddsPlan(
        fix_match=match_info,
        company_list=company_list,
    )


@tool(parse_docstring=True)
def get_odds_info_for_match(plan: MatchOddsPlan) -> Optional[BasedMatchOddsInfo]:
    """
    根据已经解析好的赔率查询计划（比赛信息 + 公司列表）请求赔率数据。

    Args:
        plan (MatchOddsPlan): 由 plan_match_odds_query 生成的查询计划。

    Returns:
        Optional[BasedMatchOddsInfo]: 某场比赛的赔率信息。
    """
    logger.info(">>> [Tool] get_odds_info_for_match 被调用")
    odds_info = get_odds_for_match(plan.fix_match, plan.company_list)
    return odds_info
