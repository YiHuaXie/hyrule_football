from pydantic import BaseModel, Field, model_validator, field_validator
from typing_extensions import Annotated


class MatchInfo(BaseModel):
    """生成赛事信息模型"""

    season: Annotated[str, Field(..., description="赛季")]

    league: Annotated[str, Field(..., description="联赛")]
    league_id: Annotated[str, Field(..., description="联赛ID")]
    league_round: Annotated[str, Field(..., description="轮次")]

    match_id: Annotated[str, Field(..., description="比赛ID")]
    match_time: Annotated[int, Field(..., description="比赛时间")]
    match_state: Annotated[int, Field(..., description="比赛状态")]
    match_state_show: Annotated[str, Field(default="", description="比赛状态文字")]

    home: Annotated[str, Field(..., description="主队")]
    home_rank: Annotated[str, Field(..., description="主队排名")]
    home_id: Annotated[str, Field(..., description="主队ID")]

    away: Annotated[str, Field(..., description="客队")]
    away_id: Annotated[str, Field(..., description="客队ID")]
    away_rank: Annotated[str, Field(..., description="客队排名")]

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
            "leagueId": "league_id",
            "round": "league_round",
            "matchTime": "match_time",
            "homeTeamId": "home_id",
            "awayTeamId": "away_id",
            "homeRank": "home_rank",
            "awayRank": "away_rank",
            "matchState": "match_state",
            "matchStateShow": "match_state_show",
        }

    @model_validator(mode="before")
    @classmethod
    def model_validate(cls, values: dict):
        for k, v in cls._alias_map().items():
            if k in values and v not in values:
                values[v] = values[k]
                del values[k]

        return values

    @field_validator("match_id", "league_id", "home_id", "away_id", mode="before")
    def to_string(cls, v):
        return v if isinstance(v, str) else str(v)
