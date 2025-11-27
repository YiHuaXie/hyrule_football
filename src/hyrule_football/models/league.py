from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing_extensions import Annotated, Optional
from typing import List


class LeagueModel(BaseModel):
    """联赛模型"""

    model_config = ConfigDict(populate_by_name=True)

    league_id: Annotated[str, Field(..., description="联赛ID", alias="leagueId")]
    league_name: Annotated[str, Field(..., description="联赛名称", alias="leagueName")]
    cup: Annotated[Optional[str], Field(default=None, description="杯赛标记，1为杯赛")]

    @property
    def is_cup(self) -> bool:
        return self.cup == "1"

    @field_validator("league_id", "cup", mode="before")
    def to_string(cls, v):
        return v if isinstance(v, str) else str(v)

    @staticmethod
    def from_dict(data: dict):
        return LeagueModel(**data)
