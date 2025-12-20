from pydantic import BaseModel, Field, model_validator
from typing_extensions import Annotated


class StandardOddsBase(BaseModel):
    """生成欧洲指数（简称欧指）和亚洲盘口（简称亚盘）赔率对比模型"""

    system: Annotated[str, Field(..., description="体系名称")]
    interval: Annotated[str, Field(..., description="区间")]
    w: Annotated[float, Field(..., description="欧指-胜赔率(Win)")]
    d: Annotated[float, Field(..., description="欧指-平赔率(Draw)")]
    l: Annotated[float, Field(..., description="欧指-负赔率(Lose)")]
    return_rate: Annotated[float, Field(..., description="返还率(%)")]
    goal_line: Annotated[float, Field(..., description="亚盘-让球盘口")]
    water_level: Annotated[str, Field(..., description="亚盘-水位（赔率）")]

    model_config = {
        "populate_by_name": True,  # 支持英文字段名或别名
    }


class StandardOddsEuroRange(BaseModel):
    """生成胜平负赔率标准范围模型"""

    low_w: Annotated[float, Field(..., description="胜赔率(Win) 低位")]
    hight_w: Annotated[float, Field(..., description="胜赔率(Win) 高位")]
    low_d: Annotated[float, Field(..., description="平赔率(Draw) 低位")]
    hight_d: Annotated[float, Field(..., description="平赔率(Draw) 高位")]
    low_l: Annotated[float, Field(..., description="负赔率(Lose) 低位")]
    hight_l: Annotated[float, Field(..., description="负赔率(Lose) 高位")]

    @classmethod
    def from_standard_odds_list(cls, odds_list: list[StandardOddsBase]):
        w_list = [odds.w for odds in odds_list]
        d_list = [odds.d for odds in odds_list]
        l_list = [odds.l for odds in odds_list]

        return StandardOddsEuroRange(
            low_w=min(w_list),
            hight_w=max(w_list),
            low_d=min(d_list),
            hight_d=max(d_list),
            low_l=min(l_list),
            hight_l=max(l_list),
        )

    @property
    def range_description(self) -> str:
        """获取范围表述字段"""

        return f"胜范围: {self.low_w} ~ {self.hight_w}, 平范围: {self.low_d} ~ {self.hight_d}, 负范围: {self.low_l} ~ {self.hight_l}"
