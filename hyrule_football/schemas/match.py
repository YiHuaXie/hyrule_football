from pydantic import BaseModel, Field, model_validator, field_validator
from typing import Optional, Dict
from datetime import datetime, timedelta
from hyrule_football.utils import match_league_name, TeamMatcher


class MatchBase(BaseModel):
    """生成赛事信息模型"""

    oh_league_id: str = Field(..., description="欧核联赛ID", alias="leagueId")
    oh_match_id: str = Field(..., description="欧核比赛ID", alias="matchId")
    oh_home_team_id: str = Field(..., description="欧核主队ID", alias="homeTeamId")
    oh_away_team_id: str = Field(..., description="欧核客队ID", alias="awayTeamId")

    dqd_match_id: Optional[str] = Field(default=None, description="懂球帝比赛ID")
    dqd_home_team_id: Optional[str] = Field(default=None, description="懂球帝主队ID")
    dqd_away_team_id: Optional[str] = Field(default=None, description="客队懂球帝球队ID")

    season: str = Field(..., description="赛季")
    league: str = Field(..., description="联赛")
    league_round: str = Field(..., description="轮次", alias="round")

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

    match_state_show: str = Field(
        default="",
        description="比赛状态文字",
        alias="matchStateShow",
    )

    home: str = Field(..., description="主队", alias="homeTeam")
    home_rank: str = Field(..., description="主队排名", alias="homeRank")

    away: str = Field(..., description="客队", alias="awayTeam")
    away_rank: str = Field(..., description="客队排名", alias="awayRank")

    model_config = {
        "populate_by_name": True,
    }

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

    @field_validator(
        "oh_league_id",
        "oh_match_id",
        "oh_home_team_id",
        "oh_away_team_id",
        "dqd_match_id",
        "dqd_home_team_id",
        "dqd_away_team_id",
        mode="before",
    )
    def to_string(cls, v):
        return v if isinstance(v, str) else str(v)

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
                }
            ),
            "league_id": league_id,
            "home_id": home_id,
            "away_id": away_id,
        }


class DQDMatch(BaseModel):
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

    def __init__(self, match: MatchBase):
        self.match = match

    def merge_dqd_match(self, dqd: DQDMatch) -> bool:
        """合并懂球帝比赛信息"""
        if match_league_name(dqd.competition_name) != self.match.league:
            return False
        if dqd.start_play != self.match.match_time:
            return False

        # 判断两场比赛的球队是否匹配，并识别哪个是主场
        matched, home_team = TeamMatcher().is_match(
            self.match.home,
            self.match.away,
            team_a=dqd.team_A_name,
            team_b=dqd.team_B_name,
        )

        if matched and home_team == "team_a":
            self.match.dqd_match_id = dqd.match_id
            self.match.dqd_home_team_id = dqd.team_A_id
            self.match.dqd_away_team_id = dqd.team_B_id
            return True

        if matched and home_team == "team_b":
            self.match.dqd_match_id = dqd.match_id
            self.match.dqd_home_team_id = dqd.team_B_id
            self.match.dqd_away_team_id = dqd.team_A_id
            return True

        return False
