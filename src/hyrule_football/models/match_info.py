from pydantic import BaseModel, Field, model_validator
from typing_extensions import Annotated


class MatchInfo(BaseModel):
    """生成赛事信息模型"""

    home: Annotated[str, Field(..., description="主队")]
    away: Annotated[str, Field(..., description="客队")]
    match_id: Annotated[str, Field(..., description="比赛ID")]
    league: Annotated[str, Field(..., description="联赛")]
    matchStateShow: Annotated[str, Field(..., description="比赛状态")]

    @property
    def match_description(self) -> str:
        """生成赛事介绍"""
        return f"{self.home}(主) VS {self.away}(客)"

    @classmethod
    def _alias_map(cls):
        return {
            "homeTeam": "home",
            "awayTeam": "away",
            "matchId": "match_id",
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
