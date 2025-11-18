from pydantic import BaseModel, Field, model_validator
from typing_extensions import Annotated


class StandardOdds(BaseModel):
    """生成欧洲指数（简称欧指）和亚洲盘口（简称亚盘）赔率对比模型"""

    system: Annotated[str, Field(..., description="体系名称", alias="体系")]
    interval: Annotated[str, Field(..., description="区间", alias="区间")]
    w: Annotated[float, Field(..., description="欧指-胜赔率(Win)", alias="胜")]
    d: Annotated[float, Field(..., description="欧指-平赔率(Draw)", alias="平")]
    l: Annotated[float, Field(..., description="欧指-负赔率(Lose)", alias="负")]
    return_rate: Annotated[float, Field(..., description="返还率(%)", alias="返还率")]
    goal_line: Annotated[float, Field(..., description="亚盘-让球盘口", alias="让球盘口")]
    water_level: Annotated[str, Field(..., description="亚盘-水位（赔率）", alias="水位")]

    model_config = {
        "populate_by_name": True,  # 支持英文字段名或别名
        "json_schema_extra": {
            "examples": [
                {"system": "西甲95"},
                {"interval": "0区"},
                {"w": 1.38},
                {"d": 4.4},
                {"l": 8.0},
                {"return_rate": 94.5},
                {"goal_line": -1.25},
                {"water_level": "低"},
            ]
        },
    }

    @property
    def markdown_text(self):
        return f"{self.system} | {self.interval} | {self.w} | {self.d} | {self.l} | {self.return_rate} | {self.goal_line} | {self.water_level} |"

    @model_validator(mode="before")
    @classmethod
    def model_validate(cls, values: dict):
        # 把别名填充到英文字段名
        for k, v in cls._alias_map().items():
            if k in values and v not in values:
                values[v] = values[k]
                del values[k]
        # print(values)

        # 校验字段是否缺失
        for field in cls._required_fields():
            if field not in values:
                raise ValueError(f"❌ 缺少 {field} 的值")

        values["system"] = values["system"].replace("体系", "")

        # 数值字段转换
        for field in ["w", "d", "l", "return_rate", "goal_line"]:
            try:
                float_value = float(values[field])
                float_value = 0.0 if float_value == 0.0 else float_value
                values[field] = float_value
            except (TypeError, ValueError):
                raise ValueError(f"❌ 字段 {field} 必须是数字，当前值: {values[field]}")

        if values["w"] < 1.0:
            raise ValueError("❌ 欧指-胜赔率不能小于1.0")
        if values["d"] < 1.0:
            raise ValueError("❌ 欧指-平赔率不能小于1.0")
        if values["l"] < 1.0:
            raise ValueError("❌ 欧指-负赔率不能小于1.0")
        if values["return_rate"] < 0 or values["return_rate"] > 100:
            raise ValueError("❌ 返还率(%)必须在0到100之间")
        return values

    @classmethod
    def _alias_map(cls):
        return {
            "体系": "system",
            "区间": "interval",
            "h": "w",
            "胜": "w",
            "平": "d",
            "a": "l",
            "负": "l",
            "返还率": "return_rate",
            "让球盘口": "goal_line",
            "水位": "water_level",
        }

    @classmethod
    def _required_fields(cls):
        return [
            "system",
            "interval",
            "w",
            "d",
            "l",
            "return_rate",
            "goal_line",
            "water_level",
        ]


class EuroStandardOddsRange(BaseModel):
    """生成胜平负赔率标准范围模型"""

    low_w: Annotated[float, Field(..., description="胜赔率(Win) 低位")]
    hight_w: Annotated[float, Field(..., description="胜赔率(Win) 高位")]
    low_d: Annotated[float, Field(..., description="平赔率(Draw) 低位")]
    hight_d: Annotated[float, Field(..., description="平赔率(Draw) 高位")]
    low_l: Annotated[float, Field(..., description="负赔率(Lose) 低位")]
    hight_l: Annotated[float, Field(..., description="负赔率(Lose) 高位")]

    @property
    def range_description(self) -> str:
        """获取范围表述字段"""

        return f"胜范围: {self.low_w} ~ {self.hight_w}, 平范围: {self.low_d} ~ {self.hight_d}, 负范围: {self.low_l} ~ {self.hight_l}"
