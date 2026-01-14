from pydantic import BaseModel, Field, field_validator
from typing import ClassVar, Tuple, Optional
from hyrule_football.utils import dqd_team_id_from_dqd


class TeamSchemaDTO(BaseModel):
    id: int
    name: str
    oh_id: int
    dqd_id: Optional[str] = None

    model_config = {
        "from_attributes": True,
    }


class TeamSchemaRank(BaseModel):
    """球队排名模型"""

    # 排名不准 不能用排名做参考
    TEAM_STAT_FIELDS: ClassVar[Tuple[str, ...]] = (
        "matches_total",
        "w",
        "d",
        "l",
        "goals_pro",
        "goals_against",
        "points",
    )

    id: int = Field(default=0, description="球队ID")
    name: str = Field(default="", description="球队名称")
    rank: str = Field(default="", description="球队排名")

    matches_total: int = Field(default=0, description="场次")
    w: int = Field(default=0, description="胜场")
    d: int = Field(default=0, description="平场")
    l: int = Field(default=0, description="负场")

    goals_pro: int = Field(default=0, description="进球")
    goals_against: int = Field(default=0, description="失球")
    points: int = Field(default=0, description="积分")

    @property
    def goal_diff(self) -> int:
        return self.goals_pro - self.goals_against

    @property
    def not_started(self) -> bool:
        return all(getattr(self, f) == 0 for f in self.TEAM_STAT_FIELDS)

    @field_validator("rank", mode="before")
    def convert_to_str(cls, v):
        if not v:
            return ""
        try:
            return str(v)
        except (ValueError, TypeError):
            return ""

    @field_validator("*", mode="before")
    def covert_to_int(cls, v, info):
        if info.field_name in ["name", "rank"]:
            return v
        if not v:
            return 0
        try:
            return int(v)
        except (ValueError, TypeError):
            return 0

    def _stat_fingerprint(self) -> tuple[int, ...]:
        return tuple(getattr(self, f) for f in self.TEAM_STAT_FIELDS)

    @staticmethod
    def is_same_team(team1: "TeamSchemaRank", team2: "TeamSchemaRank") -> bool:
        """判断两个球队是否为同一支球队"""
        # 这个算法有限制，对于完赛的赛季通过积分榜判断是否为同一支球队是大概率的准确的
        # 如果赛季刚开始，指纹数据就不是很准了
        if team1.name and team2.name and team1.name == team2.name:
            return True

        if team1.not_started or team2.not_started:
            return False

        return team1._stat_fingerprint() == team2._stat_fingerprint()

    @classmethod
    def from_source(cls, data: dict, mapping: dict) -> "TeamSchemaRank":
        return cls(**{field: data.get(src) for field, src in mapping.items()})

    @classmethod
    def from_dqd_dict(cls, data: dict) -> "TeamSchemaRank":
        data["team_id"] = dqd_team_id_from_dqd(data.get("team_id"))

        DQD_MAPPING = {
            "id": "team_id",
            "name": "team_name",
            "rank": "rank",
            "matches_total": "matches_total",
            "w": "matches_won",
            "d": "matches_draw",
            "l": "matches_lost",
            "goals_pro": "goals_pro",
            "goals_against": "goals_against",
            "points": "points",
        }

        return cls.from_source(data, DQD_MAPPING)

    @classmethod
    def from_oh_dict(cls, data: dict) -> "TeamSchemaRank":
        OH_MAPPING = {
            "id": "teamId",
            "name": "teamName",
            "rank": "rank",
            "matches_total": "round",
            "w": "win",
            "d": "draw",
            "l": "lose",
            "goals_pro": "winGoals",
            "goals_against": "loseGoals",
            "points": "score",
        }
        return cls.from_source(data, OH_MAPPING)
