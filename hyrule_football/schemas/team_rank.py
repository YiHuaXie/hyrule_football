from pydantic import BaseModel, Field, field_validator
from typing import ClassVar, Tuple


class TeamRankSchema(BaseModel):
    """球队排名模型"""

    # 排名不准  不能用排名做参考
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
    def is_same_team(team1: "TeamRankSchema", team2: "TeamRankSchema") -> bool:
        if team1.id and team2.id and team1.id == team2.id:
            return True

        if team1.name and team2.name and team1.name == team2.name:
            return True

        if team1.not_started or team2.not_started:
            return False

        return team1._stat_fingerprint() == team2._stat_fingerprint()

    @classmethod
    def from_source(cls, data: dict, mapping: dict) -> "TeamRankSchema":
        return cls(**{field: data.get(src) for field, src in mapping.items()})

    @classmethod
    def from_dqd_dict(cls, data: dict) -> "TeamRankSchema":
        team_id = data.get("team_id")
        if team_id:
            try:
                team_id = int(team_id)
                if team_id > 50000000:
                    data["team_id"] = team_id - 50000000
            except (ValueError, TypeError):
                pass

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

        try:
            return cls.from_source(data, DQD_MAPPING)
        except Exception as e:
            print(f"❌ TeamRankSchema received invalid data: {e}")
            return cls()

    @classmethod
    def from_oh_dict(cls, data: dict) -> "TeamRankSchema":
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
