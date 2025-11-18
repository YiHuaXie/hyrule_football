from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from typing_extensions import Annotated
from .match import MatchInfo
from hyrule_football.utils import water_level_str, asia_handicap_float


class Company(BaseModel):
    """博彩公司模型"""

    cid: Annotated[int, Field(..., description="博彩公司ID")]
    name: Annotated[str, Field(..., description="博彩公司名称")]

    @classmethod
    def bet635(cls):
        return cls(cid=38, name="bet365")

    @classmethod
    def williamhill(cls):
        return cls(cid=26, name="威廉希尔")


class AsiaOdds(BaseModel):
    """生成亚盘(让球盘口+水位)赔率模型"""

    goal_line: Annotated[float, Field(..., description="让球盘口")]
    water_level: Annotated[str, Field(..., description="水位（赔率）")]
    return_rate: Annotated[float, Field(..., description="返还率")]

    @field_validator("water_level", mode="before")
    def to_water_level(cls, v):
        return water_level_str(v)

    @field_validator("goal_line", mode="before")
    def to_goal_line(cls, v):
        if isinstance(v, float):
            v = 0.0 if v == 0.0 else v
            return v
        return asia_handicap_float(v)


class EuroOdds(BaseModel):
    """生成欧指(胜平负)赔率模型"""

    w: Annotated[float, Field(..., description="胜赔率(Win)")]
    d: Annotated[float, Field(..., description="平赔率(Draw)")]
    l: Annotated[float, Field(..., description="负赔率(Lose)")]
    return_rate: Annotated[float, Field(..., description="返还率")]

    @field_validator("w", "d", "l", "return_rate", mode="before")
    def to_float(cls, v):
        return v if isinstance(v, float) else float(v)

    @property
    def opposite_odds(self):
        # 生成对立面的欧指
        return EuroOdds(w=self.l, d=self.d, l=self.w, return_rate=self.return_rate)


class OddsSummary(BaseModel):
    """生成「指定的博彩公司针对某支球队给出的欧指和亚盘赔率汇总模型」"""

    company: Annotated[Company, Field(..., description="博彩公司")]

    team_name: Annotated[str, Field(..., description="球队名称")]

    init_euro: Annotated[
        Optional[EuroOdds],
        Field(default=None, description="开盘欧指赔率"),
    ]

    init_asia: Annotated[
        Optional[AsiaOdds],
        Field(default=None, description="开盘亚盘赔率"),
    ]

    now_euro: Annotated[
        Optional[EuroOdds],
        Field(default=None, description="当前欧指赔率"),
    ]

    now_asia: Annotated[
        Optional[AsiaOdds],
        Field(default=None, description="当前亚盘赔率"),
    ]

    euro_history: Annotated[
        List[EuroOdds],
        Field(default_factory=list, description="历史欧指赔率列表"),
    ]

    asia_history: Annotated[
        List[EuroOdds],
        Field(default_factory=list, description="历史亚盘列表"),
    ]


class BasedMatchOddsInfo(BaseModel):
    """生成「某场比赛相关博彩公司的欧指和亚盘赔率信息模型」"""

    match_info: Annotated[
        MatchInfo,
        Field(..., description="赛事信息"),
    ]

    company_list: Annotated[
        List[Company],
        Field(default_factory=list, description="博彩公司列表"),
    ]

    home_summary_list: Annotated[
        List[OddsSummary],
        Field(default_factory=list, description="主队赔率汇总列表"),
    ]

    away_summary_list: Annotated[
        List[OddsSummary],
        Field(default_factory=list, description="客队赔率汇总列表"),
    ]
