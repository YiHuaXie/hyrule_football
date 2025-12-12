from pydantic import BaseModel, Field, model_validator, field_validator
from typing_extensions import Annotated
from typing import Optional, Dict
from datetime import datetime, timedelta
from hyrule_football.utils import match_league_name, TeamMatcher


class MatchInfo(BaseModel):
    """生成赛事信息模型"""

    season: Annotated[str, Field(..., description="赛季")]

    league: Annotated[str, Field(..., description="联赛")]
    league_id: Annotated[str, Field(..., description="联赛ID")]
    league_round: Annotated[str, Field(..., description="轮次")]

    match_id: Annotated[str, Field(..., description="比赛ID")]
    dqd_match_id: Annotated[Optional[str], Field(default=None, description="懂球帝比赛ID")]

    match_time: Annotated[str, Field(..., description="比赛时间,（格式：YYYY-MM-DD HH:MM）")]
    match_state: Annotated[int, Field(..., description="比赛状态, 0:未开赛, 1:进行中, 2:已完赛")]
    match_state_show: Annotated[str, Field(default="", description="比赛状态文字")]

    home: Annotated[str, Field(..., description="主队")]
    home_rank: Annotated[str, Field(..., description="主队排名")]
    home_id: Annotated[str, Field(..., description="主队ID")]
    home_dqd_team_id: Annotated[Optional[str], Field(default=None, description="主队懂球帝球队ID")]

    away: Annotated[str, Field(..., description="客队")]
    away_id: Annotated[str, Field(..., description="客队ID")]
    away_rank: Annotated[str, Field(..., description="客队排名")]
    away_dqd_team_id: Annotated[Optional[str], Field(default=None, description="客队懂球帝球队ID")]

    @field_validator("match_time", mode="before")
    def convert_timestamp_to_str(cls, v):
        dt = datetime.fromtimestamp(v / 1000)
        return dt.strftime("%Y-%m-%d %H:%M")

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

    @field_validator(
        "match_id",
        "dqd_match_id",
        "league_id",
        "home_id",
        "home_dqd_team_id",
        "away_id",
        "away_dqd_team_id",
        mode="before",
    )
    def to_string(cls, v):
        return v if isinstance(v, str) else str(v)


class MatchModel(BaseModel):
    """生成赛事信息模型"""

    season: Annotated[str, Field(..., description="赛季")]

    league: Annotated[str, Field(..., description="联赛")]
    league_id: Annotated[str, Field(..., description="联赛ID")]
    league_round: Annotated[str, Field(..., description="轮次")]

    match_id: Annotated[str, Field(..., description="比赛ID")]
    dqd_match_id: Annotated[Optional[str], Field(default=None, description="懂球帝比赛ID")]

    match_time: Annotated[str, Field(..., description="比赛时间,（格式：YYYY-MM-DD HH:MM）")]
    match_state: Annotated[
        int,
        Field(..., description="比赛状态, 0:未开赛, 1:进行中, 2:已完赛 4:腰斩"),
    ]
    match_state_show: Annotated[str, Field(default="", description="比赛状态文字")]

    home: Annotated[str, Field(..., description="主队")]
    home_rank: Annotated[str, Field(..., description="主队排名")]
    home_id: Annotated[str, Field(..., description="主队ID")]
    home_dqd_team_id: Annotated[Optional[str], Field(default=None, description="主队懂球帝球队ID")]

    away: Annotated[str, Field(..., description="客队")]
    away_id: Annotated[str, Field(..., description="客队ID")]
    away_rank: Annotated[str, Field(..., description="客队排名")]
    away_dqd_team_id: Annotated[Optional[str], Field(default=None, description="客队懂球帝球队ID")]

    @field_validator("match_time", mode="before")
    def convert_timestamp_to_str(cls, v):
        dt = datetime.fromtimestamp(v / 1000)
        return dt.strftime("%Y-%m-%d %H:%M")

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

    @field_validator(
        "match_id",
        "dqd_match_id",
        "league_id",
        "home_id",
        "home_dqd_team_id",
        "away_id",
        "away_dqd_team_id",
        mode="before",
    )
    def to_string(cls, v):
        return v if isinstance(v, str) else str(v)


class DQDMatchModel(BaseModel):
    """懂球帝比赛信息模型"""

    match_id: str = Field(..., description="比赛ID")
    competition: Dict = Field(..., description="联赛信息")
    start_play: str = Field(..., description="比赛时间")
    team_A: Dict = Field(..., description="主队信息")
    team_B: Dict = Field(..., description="客队信息")

    @field_validator("start_play", mode="before")
    def convert_datetime(cls, v):
        dt = datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
        dt = dt.replace(second=0)  # 或者直接解析 "%Y-%m-%d %H:%M"
        dt_plus_8h = dt + timedelta(hours=8)
        return dt_plus_8h.strftime("%Y-%m-%d %H:%M")

    @property
    def team_A_name(self) -> str:
        return self.team_A.get("name", "")

    @property
    def team_B_name(self) -> str:
        return self.team_B.get("name", "")

    @property
    def team_A_id(self) -> str:
        return self.team_A.get("id", "")

    @property
    def team_B_id(self) -> str:
        return self.team_B.get("id", "")

    @property
    def competition_id(self) -> str:
        return self.competition.get("id", "")

    @property
    def competition_name(self) -> str:
        return self.competition.get("name", "")


class MatchMatcher:
    """比赛信息匹配器"""

    def __init__(self, match: MatchModel):
        self.match = match

    def merge_dqd_match(self, dqd: DQDMatchModel) -> bool:
        """合并懂球帝比赛信息"""
        if match_league_name(dqd.competition_name) != self.match.league:
            return False
        if dqd.start_play != self.match.match_time:
            return False

        matched, home_team = TeamMatcher().is_match(
            self.match.home,
            self.match.away,
            team_a=dqd.team_A_name,
            team_b=dqd.team_B_name,
        )

        if matched and home_team == "team_a":
            self.match.dqd_match_id = dqd.match_id
            self.match.home_dqd_team_id = dqd.team_A_id
            self.match.away_dqd_team_id = dqd.team_B_id
            return True

        if matched and home_team == "team_b":
            self.match.dqd_match_id = dqd.match_id
            self.match.home_dqd_team_id = dqd.team_B_id
            self.match.away_dqd_team_id = dqd.team_A_id
            return True

        return False
