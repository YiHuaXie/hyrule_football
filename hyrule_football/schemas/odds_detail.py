from typing import Optional, List
from pydantic import BaseModel, Field
from typing_extensions import Annotated
from .match import MatchBase
from .company import CompanyModel
from .euro_odds import EuroOdds
from .asia_odds import AsiaOdds


class OddsSummary(BaseModel):
    """生成「赔率汇总模型」"""

    cid: Annotated[int, Field(..., description="博彩公司ID")]

    team_name: Annotated[str, Field(..., description="球队名称")]

    init_euro: Annotated[Optional[EuroOdds], Field(default=None, description="初始欧指")]

    init_asia: Annotated[Optional[AsiaOdds], Field(default=None, description="初始亚盘")]

    now_euro: Annotated[Optional[EuroOdds], Field(default=None, description="即时欧指")]

    now_asia: Annotated[Optional[AsiaOdds], Field(default=None, description="即时亚盘")]

    euro_history: Annotated[List[EuroOdds], Field(default_factory=list, description="历史欧指")]

    asia_history: Annotated[List[AsiaOdds], Field(default_factory=list, description="历史亚盘")]


class OddsPattern(BaseModel):
    """生成「欧指格局模型」"""

    cid: Annotated[int, Field(..., description="博彩公司ID")]

    init_team_name: Annotated[Optional[str], Field(default=None, description="初始让球方")]

    now_team_name: Annotated[Optional[str], Field(default=None, description="即时让球方")]

    init_pattern: Annotated[
        Optional[str],
        Field(default=None, description="初始欧指格局，例如: 低-中-高"),
    ]

    now_pattern: Annotated[
        Optional[str],
        Field(default=None, description="即时欧指格局，例如: 低-中-高"),
    ]


class MatchOddsDetail(BaseModel):
    """生成「某场比赛相关博彩公司的欧指和亚盘赔率信息模型」"""

    match_base: Annotated[MatchBase, Field(..., description="赛事信息")]

    company_list: Annotated[
        List[CompanyModel],
        Field(default_factory=list, description="博彩公司列表"),
    ]

    odds_pattern_list: Annotated[
        List[OddsPattern],
        Field(default_factory=list, description="「欧指格局模型」列表"),
    ]

    home_summary_list: Annotated[
        List[OddsSummary],
        Field(default_factory=list, description="主队「赔率汇总模型」列表"),
    ]

    away_summary_list: Annotated[
        List[OddsSummary],
        Field(default_factory=list, description="客队「赔率汇总模型」列表"),
    ]
