from pydantic import BaseModel, Field, field_validator, model_validator

_START_STAT_FIELDS = ("matches_total", "w", "d", "l", "goals_pro", "goals_against", "points")

# 排名不准  不能用排名做参考
_TEAM_STAT_FIELDS = ("matches_total", "w", "d", "l", "goals_pro", "goals_against", "points")


class TeamStat(BaseModel):
    """球队数据统计模型"""

    id: int = Field(..., description="球队ID")
    name: str = Field(..., description="球队名称")
    rank: int = Field(default=0, description="球队排名")

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
        return all(getattr(self, f) == 0 for f in _START_STAT_FIELDS)

    @field_validator(
        "id",
        "matches_total",
        "w",
        "d",
        "l",
        "goals_pro",
        "goals_against",
        "points",
        "rank",
        mode="before",
    )
    def covert_to_int(cls, v):
        try:
            return int(v)
        except ValueError:
            return 0

    def _stat_fingerprint(self) -> tuple[int, ...]:
        return tuple(getattr(self, f) for f in _TEAM_STAT_FIELDS)

    # def _weak_fingerprint(self) -> tuple[int, ...]:
    #     return tuple(getattr(self, f) for f in _WEAK_STAT_FIELDS)

    @staticmethod
    def is_same_team(team1: "TeamStat", team2: "TeamStat") -> bool:
        if team1.id and team2.id and team1.id == team2.id:
            return True

        if team1.name and team2.name and team1.name == team2.name:
            return True

        if team1.not_started or team2.not_started:
            return False

        if team1._stat_fingerprint() == team2._stat_fingerprint():
            return True

        # if team1._weak_fingerprint() == team2._weak_fingerprint():
        #     return True

        return False

    @staticmethod
    def adpate_dqd_team_stat(stat: dict) -> "TeamStat":
        values = {
            "id": stat.get("team_id"),
            "name": stat.get("team_name"),
            "rank": stat.get("rank"),
            "matches_total": stat.get("matches_total"),
            "w": stat.get("matches_won"),
            "d": stat.get("matches_draw"),
            "l": stat.get("matches_lost"),
            "goals_pro": stat.get("goals_pro"),
            "goals_against": stat.get("goals_against"),
            "points": stat.get("points"),
        }
        return TeamStat(**values)

    @staticmethod
    def adpate_oh_team_stat(stat: dict) -> "TeamStat":
        values = {
            "id": stat.get("teamId"),
            "name": stat.get("teamName"),
            "rank": stat.get("rank"),
            "matches_total": stat.get("round"),
            "w": stat.get("win"),
            "d": stat.get("draw"),
            "l": stat.get("lose"),
            "goals_pro": stat.get("winGoals"),
            "goals_against": stat.get("loseGoals"),
            "points": stat.get("score"),
        }

        return TeamStat(**values)
