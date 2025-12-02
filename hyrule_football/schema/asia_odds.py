from pydantic import BaseModel, Field, field_validator
from typing_extensions import Annotated
from hyrule_football.utils import water_level_str, asia_handicap_float


class AsiaOdds(BaseModel):
    """生成亚盘(让球盘口+水位)赔率模型"""

    goal_line: Annotated[float, Field(..., description="让球盘口")]
    water_level: Annotated[str, Field(..., description="水位（赔率）")]
    return_rate: Annotated[float, Field(..., description="返还率")]

    @field_validator("water_level", mode="before")
    def to_water_level(cls, v):
        return water_level_str(v)

    @field_validator("goal_line", mode="before")
    def to_goal_line(cls, v):
        if isinstance(v, float):
            v = 0.0 if v == 0.0 else v
            return v
        return asia_handicap_float(v)

    @property
    def flipped_goal_line(self) -> float:
        flipped = self.goal_line * -1
        return 0.0 if flipped == 0.0 else flipped
