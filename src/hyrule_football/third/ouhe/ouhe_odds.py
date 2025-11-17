from pydantic import BaseModel, Field
from typing_extensions import Annotated
from hyrule_football.utils import parse_asia_handicap_smart, water_level_standadrd_str


class OHEuroOdds(BaseModel):
    """三方平台-欧指赔率模型，包括博彩公司ID，初始HAD 和 即时HAD"""

    matchId: Annotated[str, Field(..., description="比赛ID")]
    cid: Annotated[str, Field(..., description="博彩公司ID")]
    initOddsWin: Annotated[str, Field(..., description="欧指-初始主胜(H)赔率")]
    initOddsDraw: Annotated[str, Field(..., description="欧指-初始平局(D)赔率")]
    initOddsLose: Annotated[str, Field(..., description="欧指-初始客胜(A)赔率")]
    initReturnRates: Annotated[str, Field(..., description="初始返还率")]
    nowOddsWin: Annotated[str, Field(..., description="欧指-即时主胜(H)赔率")]
    nowOddsDraw: Annotated[str, Field(..., description="欧指-即时平局(D)赔率")]
    nowOddsLose: Annotated[str, Field(..., description="欧指-即时客胜(A)赔率")]
    nowReturnRates: Annotated[str, Field(..., description="即时初始返还率")]


class OHAsiaOdds(BaseModel):
    """三方平台-亚盘赔率模型，包括博彩公司ID，初始盘口+水位和即时盘口+水位"""

    matchId: Annotated[str, Field(default="", description="比赛ID")]
    cid: Annotated[str, Field(default="", description="博彩公司ID")]
    initBet: Annotated[str, Field(default="", description="亚盘-初始盘口")]
    initOddsWin: Annotated[str, Field(default="", description="亚盘-初始主胜赔率")]
    initOddsLose: Annotated[str, Field(default="", description="亚盘-初始客胜赔率")]
    initReturnRates: Annotated[str, Field(default="", description="亚盘-初始返还率")]
    nowBet: Annotated[str, Field(default="", description="亚盘-即时盘口")]
    nowOddsWin: Annotated[str, Field(default="", description="亚盘-即时主胜赔率")]
    nowOddsLose: Annotated[str, Field(default="", description="亚盘-即时客胜赔率")]
    nowReturnRates: Annotated[str, Field(default="", description="亚盘即时初始返还率")]

    @property
    def initGoalLine(self) -> float:
        """标准化初始让球数据，返回数字"""
        return parse_asia_handicap_smart(self.initBet)

    @property
    def nowGoalLine(self) -> float:
        """标准化即时让球数据，返回数字"""
        return parse_asia_handicap_smart(self.nowBet)

    @property
    def initWaterLevel(self) -> str:
        """标准化初始水位数据，返回低/中/高"""
        return water_level_standadrd_str(self.initOddsWin)

    @property
    def nowWaterLevel(self) -> str:
        """标准化即时水位数据，返回低/中/高"""
        return water_level_standadrd_str(self.nowOddsWins)
