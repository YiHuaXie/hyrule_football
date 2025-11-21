from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from typing_extensions import Annotated
from hyrule_football.utils import water_level_str, asia_handicap_float
from .match_info import MatchInfo
from .company import Company


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
        """生成对立面的欧指"""
        return EuroOdds(w=self.l, d=self.d, l=self.w, return_rate=self.return_rate)

    @property
    def euro_system_no(self) -> int:
        """获取欧指体系编号"""
        # 每个区间宽度：1，offset 0.8 让区间精准对应
        # 起始区间：88.2 对应体系 89
        # 所以 (88.2 + 0.8 → 89), (89.19 + 0.8 → 89),
        # (89.2 + 0.8 → 90), (90.19 + 0.8 → 90),...
        system_no = int(self.return_rate + 0.8)
        return system_no

    @property
    def euro_odds_under_94(self):
        """将当前欧指转换为94体系下的欧指"""

        # 1. 计算原始概率
        original_return_rate = self.euro_system_no / 100.0
        p_w = original_return_rate / self.w
        p_d = original_return_rate / self.d
        p_l = original_return_rate / self.l

        # 2. 概率归一化
        total = p_w + p_d + p_l
        p_w_norm = p_w / total
        p_d_norm = p_d / total
        p_l_norm = p_l / total

        # 3. 根据当前反推新赔率
        new_return_rate = 0.94
        n_w = new_return_rate / p_w_norm
        n_d = new_return_rate / p_d_norm
        n_l = new_return_rate / p_l_norm

        return EuroOdds(
            w=round(n_w, 2),
            d=round(n_d, 2),
            l=round(n_l, 2),
            return_rate=94.0,
        )


class OddsSummary(BaseModel):
    """生成「赔率汇总模型」"""

    company: Annotated[Company, Field(..., description="博彩公司")]

    team_name: Annotated[str, Field(..., description="球队名称")]

    init_euro: Annotated[
        Optional[EuroOdds],
        Field(default=None, description="初始欧指赔率"),
    ]

    init_asia: Annotated[
        Optional[AsiaOdds],
        Field(default=None, description="初始亚盘赔率"),
    ]

    now_euro: Annotated[
        Optional[EuroOdds],
        Field(default=None, description="即时欧指赔率"),
    ]

    now_asia: Annotated[
        Optional[AsiaOdds],
        Field(default=None, description="即时亚盘赔率"),
    ]

    euro_history: Annotated[
        List[EuroOdds],
        Field(default_factory=list, description="历史欧指赔率列表"),
    ]

    asia_history: Annotated[
        List[AsiaOdds],
        Field(default_factory=list, description="历史亚盘列表"),
    ]


class OddsPattern(BaseModel):
    """生成「欧指格局模型」"""

    company: Annotated[Company, Field(..., description="博彩公司")]

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


class BasedMatchOddsInfo(BaseModel):
    """生成「某场比赛相关博彩公司的欧指和亚盘赔率信息模型」"""

    match_info: Annotated[MatchInfo, Field(..., description="赛事信息")]

    company_list: Annotated[
        List[Company],
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
