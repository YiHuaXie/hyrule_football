from pydantic import BaseModel, Field, field_validator
from typing_extensions import Annotated
from hyrule_football.utils import water_level_str, asia_handicap_float
from typing import Tuple


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


class CombineAsiaOdds(BaseModel):
    """生成综合亚盘(主队+客队)赔率模型"""

    init_bet: Annotated[str, Field(..., description="初始盘口", alias="initBet")]
    init_odds_up: Annotated[float, Field(..., description="初始主队水位", alias="initOddsUp")]
    init_return_rate: Annotated[
        float, Field(..., description="初始返还率", alias="initReturnRates")
    ]
    init_odds_down: Annotated[float, Field(..., description="初始客队水位", alias="initOddsDown")]
    now_bet: Annotated[str, Field(..., description="即时盘口", alias="nowBet")]
    now_odds_up: Annotated[float, Field(..., description="即时主队水位", alias="nowOddsUp")]
    now_return_rate: Annotated[float, Field(..., description="即时返还率", alias="nowReturnRates")]
    now_odds_down: Annotated[float, Field(..., description="即时客队水位", alias="nowOddsDown")]

    @property
    def to_init_odds(self) -> Tuple[AsiaOdds, AsiaOdds]:
        home_odds = AsiaOdds(
            goal_line=self.init_bet,
            water_level=self.init_odds_up,
            return_rate=self.init_return_rate,
        )
        away_odds = AsiaOdds(
            goal_line=home_odds.flipped_goal_line,
            water_level=self.init_odds_down,
            return_rate=home_odds.return_rate,
        )
        return home_odds, away_odds

    @property
    def to_now_odds(self) -> Tuple[AsiaOdds, AsiaOdds]:
        home_odds = AsiaOdds(
            goal_line=self.now_bet,
            water_level=self.now_odds_up,
            return_rate=self.now_return_rate,
        )
        away_odds = AsiaOdds(
            goal_line=home_odds.flipped_goal_line,
            water_level=self.now_odds_down,
            return_rate=home_odds.return_rate,
        )
        return home_odds, away_odds
