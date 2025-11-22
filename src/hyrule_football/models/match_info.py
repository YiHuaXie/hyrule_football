from pydantic import BaseModel, Field, model_validator
from typing_extensions import Annotated


class MatchInfo(BaseModel):
    """生成赛事信息模型"""

    home: Annotated[str, Field(..., description="主队")]
    away: Annotated[str, Field(..., description="客队")]
    match_id: Annotated[str, Field(..., description="比赛ID")]
    league: Annotated[str, Field(..., description="联赛")]
    # league_round: Annotated[str, Field(..., description="轮次")]
    # match_time: Annotated[str, Field(..., description="比赛时间")]

    @property
    def match_description(self) -> str:
        """生成赛事介绍"""
        return f"{self.league}:{self.home} VS {self.away}"

    @classmethod
    def _alias_map(cls):
        return {
            "homeTeam": "home",
            "awayTeam": "away",
            "matchId": "match_id",
            # "round": "league_round",
            # "matchTime": "match_time"
        }

    @model_validator(mode="before")
    @classmethod
    def model_validate(cls, values: dict):
        for k, v in cls._alias_map().items():
            if k in values and v not in values:
                values[v] = values[k]
                del values[k]

        values["match_id"] = str(values["match_id"])

        return values


class MatchDetailInfo(BaseModel):
    """生成赛事详细信息模型"""

    # match_info: Annotated[MatchInfo, Field(..., description="赛事信息")]
    # match_time: Annotated[str, Field(..., description="比赛时间")]
    # league_round: Annotated[str, Field(..., description="轮次")]
