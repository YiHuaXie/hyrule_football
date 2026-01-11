from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, Dict
from datetime import datetime, timedelta
from hyrule_football.utils import deep_get


class MatchBase(BaseModel):
    """生成赛事信息模型"""

    oh_league_id: int = Field(..., description="欧核联赛ID", alias="leagueId")
    oh_match_id: int = Field(..., description="欧核比赛ID", alias="matchId")
    oh_home_team_id: int = Field(..., description="欧核主队ID", alias="homeTeamId")
    oh_away_team_id: int = Field(..., description="欧核客队ID", alias="awayTeamId")

    dqd_match_id: Optional[str] = Field(default=None, description="懂球帝比赛ID")
    dqd_home_team_id: Optional[str] = Field(default=None, description="懂球帝主队ID")
    dqd_away_team_id: Optional[str] = Field(default=None, description="客队懂球帝球队ID")

    season: str = Field(..., description="赛季")
    league: str = Field(..., description="联赛")
    league_round: Optional[str] = Field(default=None, description="轮次", alias="round")

    match_no: str = Field(default="", description="赛事编号，如 周日027 ", alias="matchNo")

    match_time: str = Field(
        ...,
        description="比赛时间,（格式：YYYY-MM-DD HH:MM）",
        alias="matchTime",
    )

    match_state: int = Field(
        ...,
        description="比赛状态, 0:未开赛, 1:进行中, 2:已完赛 4:腰斩",
        alias="matchState",
    )

    match_state_show: Optional[str] = Field(
        default=None,
        description="比赛状态文字",
        alias="matchStateShow",
    )

    home: str = Field(..., description="主队", alias="homeTeam")
    home_rank: Optional[str] = Field(default=None, description="主队排名", alias="homeRank")

    away: str = Field(..., description="客队", alias="awayTeam")
    away_rank: Optional[str] = Field(default=None, description="客队排名", alias="awayRank")

    model_config = {
        "populate_by_name": True,
    }

    @model_validator(mode="before")
    @classmethod
    def preprocess_values(cls, values: dict):
        if not values.get("matchNo"):
            values["matchNo"] = values.get("jsMatchNo", "")
        return values

    @field_validator("match_time", mode="before")
    def convert_timestamp_to_str(cls, v):
        # 如果已经是字符串，直接返回
        if isinstance(v, str):
            return v
        # 如果是时间戳（整数或浮点数），转换为字符串
        dt = datetime.fromtimestamp(v / 1000)
        return dt.strftime("%Y-%m-%d %H:%M")

    @property
    def match_description(self) -> str:
        """生成赛事介绍"""
        return f"{self.league}:{self.home} VS {self.away}"

    def to_db_dict(self, league_id: int, home_id: int, away_id: int) -> dict:
        """转换为数据库字典"""
        return {
            **self.model_dump(
                exclude={
                    "oh_match_id",
                    "oh_league_id",
                    "oh_home_team_id",
                    "oh_away_team_id",
                    "dqd_home_team_id",
                    "dqd_away_team_id",
                    "match_description",
                    "match_no",
                }
            ),
            "league_id": league_id,
            "home_id": home_id,
            "away_id": away_id,
        }


class DQDMatch(BaseModel):
    """懂球帝比赛信息模型"""

    match_id: str = Field(..., description="比赛ID")
    competition_name: str = Field(..., description="联赛信息")
    competition_id: str = Field(..., description="联赛ID")
    start_play: str = Field(..., description="比赛时间")
    team_A_id: str = Field(..., description="球队 A ID")
    team_B_id: str = Field(..., description="球队 B ID")
    team_A_name: str = Field(..., description="球队 A 名称")
    team_B_name: str = Field(..., description="球队 B 名称")
    team_A_rank: Optional[int] = Field(default=None, description="球队 A 联赛排名")
    team_B_rank: Optional[int] = Field(default=None, description="球队 B 联赛排名")
    home_team: Optional[str] = Field(default=None, description="主队名称")

    @model_validator(mode="before")
    @classmethod
    def preprocess_values(cls, values: dict):
        new_values = {
            "start_play": values.get("start_play"),
            "match_id": values.get("match_id"),
            "competition_id": deep_get(values, ["competition", "id"], ""),
            "competition_name": deep_get(values, ["competition", "name"], ""),
            "team_A_id": deep_get(values, ["team_A", "id"], ""),
            "team_B_id": deep_get(values, ["team_B", "id"], ""),
            "team_A_name": deep_get(values, ["team_A", "name"], ""),
            "team_B_name": deep_get(values, ["team_B", "name"], ""),
            "team_A_rank": deep_get(values, ["team_A", "league_rank"]),
            "team_B_rank": deep_get(values, ["team_B", "league_rank"]),
        }

        return new_values

    @field_validator("team_A_rank", "team_B_rank", mode="before")
    def covert_rank_to_int(cls, v):
        if not v or v == "0":
            return None

        return int(v)

    @field_validator("start_play", mode="before")
    def convert_datetime(cls, v):
        dt = datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
        dt = dt.replace(second=0)  # 或者直接解析 "%Y-%m-%d %H:%M"
        dt_plus_8h = dt + timedelta(hours=8)
        return dt_plus_8h.strftime("%Y-%m-%d %H:%M")


# class DQDMatch(BaseModel):
#     """懂球帝比赛信息模型"""

#     match_id: str = Field(..., description="比赛ID")
#     competition: Dict = Field(..., description="联赛信息")
#     start_play: str = Field(..., description="比赛时间")
#     team_A: Dict = Field(..., description="主队信息")
#     team_B: Dict = Field(..., description="客队信息")

#     @field_validator("start_play", mode="before")
#     def convert_datetime(cls, v):
#         dt = datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
#         dt = dt.replace(second=0)  # 或者直接解析 "%Y-%m-%d %H:%M"
#         dt_plus_8h = dt + timedelta(hours=8)
#         return dt_plus_8h.strftime("%Y-%m-%d %H:%M")

#     @property
#     def team_A_name(self) -> str:
#         return self.team_A.get("name", "")

#     @property
#     def team_B_name(self) -> str:
#         return self.team_B.get("name", "")

#     @property
#     def team_A_id(self) -> str:
#         return self.team_A.get("id", "")

#     @property
#     def team_B_id(self) -> str:
#         return self.team_B.get("id", "")

#     @property
#     def competition_id(self) -> str:
#         return self.competition.get("id", "")

#     @property
#     def competition_name(self) -> str:
#         return self.competition.get("name", "")
