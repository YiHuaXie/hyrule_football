from pydantic import BaseModel, Field
from typing import Optional, List, Tuple
from hyrule_football.utils import deep_get, specific_league_name
from hyrule_football.schemas.season import SeasonSchema
from hyrule_football.models import League


class LeagueSchema(BaseModel):

    id: str | int
    name: str
    is_cup: int = 0
    season: Optional[SeasonSchema] = None
    seasons: List[SeasonSchema] = []

    @staticmethod
    def from_oh_dict(data: dict) -> Optional["LeagueSchema"]:
        league_id = data.get("leagueId")
        league_name = specific_league_name(data.get("leagueName"))

        if not league_id or not league_name:
            return None

        # season = data.get("season")
        # season = SeasonSchema(league=league_name, id=season, name=season) if season else None

        seasons = data.get("seasonList", [])
        seasons = [SeasonSchema(league=league_name, id=s, name=s) for s in seasons if s]

        return LeagueSchema(
            id=league_id,
            name=league_name,
            is_cup=data.get("cup", 0),
            season=seasons[0] if seasons else None,
            seasons=seasons,
        )

    @staticmethod
    def from_dqd_dict(data: dict) -> Optional["LeagueSchema"]:
        league_id = data.get("competition_id")
        league_name = specific_league_name(data.get("label"))
        if not league_id or not league_name:
            return None

        # season_id = data.get("season_id")
        # season_name = deep_get(data, ["season", "title"])
        # if season_id and season_name:
        #     season = SeasonSchema(league=league_name, id=season_id, name=season_name)
        # else:
        #     season = None

        return LeagueSchema(id=league_id, name=league_name)


class DQDLeagueSchedule(BaseModel):
    """懂球帝联赛详情"""

    season_id: int = Field(..., description="赛季ID")
    season_name: str = Field(..., description="赛季名称")

    class Round(BaseModel):
        name: str = Field(...)
        season_id: int = Field(..., description="赛季ID")
        round_id: int = Field(..., description="轮次ID")
        gameweek: int = Field(..., description="周数")
        current: bool = Field(default=False, description="是否为当前轮次")

        @property
        def round_key(self) -> str:
            return f"{self.season_id}_{self.round_id}_{self.gameweek}"

    rounds: List[Round] = Field(..., description="轮次列表")

    @property
    def current_round_key(self) -> str:
        for r in self.rounds:
            if r.current:
                return f"{r.season_id}_{r.round_id}_{r.gameweek}"

        return ""
