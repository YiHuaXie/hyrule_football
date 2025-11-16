from pydantic import BaseModel, Field, model_validator
from typing_extensions import Annotated
from typing import List


class HYREuroOdds(BaseModel):
    """生成欧指赔率模型"""

    cid: Annotated[str, Field(default="", description="博彩公司ID")]
    match_id: Annotated[str, Field(default="", description="比赛ID")]
    h: Annotated[float, Field(..., description="主胜赔率(H)")]
    d: Annotated[float, Field(..., description="平局赔率(D)")]
    a: Annotated[float, Field(..., description="客胜赔率(A)")]


class HYRAsiaOdds(BaseModel):
    """生成亚盘赔率模型"""

    cid: Annotated[str, Field(default="", description="博彩公司ID")]
    match_id: Annotated[str, Field(default="", description="比赛ID")]
    goal_line: Annotated[float, Field(..., description="亚盘-让球盘口")]
    water_level: Annotated[str, Field(..., description="亚盘-水位（赔率）")]


class HYRStandardOdds(BaseModel):
    """生成欧洲指数（简称欧指）和亚洲盘口（简称亚盘）赔率对比模型"""

    system: Annotated[str, Field(..., description="体系名称", alias="体系")]
    interval: Annotated[str, Field(..., description="区间", alias="区间")]
    h: Annotated[float, Field(..., description="欧指-主胜赔率(H)", alias="胜")]
    d: Annotated[float, Field(..., description="欧指-平局赔率(D)", alias="平")]
    a: Annotated[float, Field(..., description="欧指-客胜赔率(A)", alias="负")]
    return_rate: Annotated[float, Field(..., description="返还率(%)", alias="返还率")]
    goal_line: Annotated[float, Field(..., description="亚盘-让球盘口", alias="让球盘口")]
    water_level: Annotated[str, Field(..., description="亚盘-水位（赔率）", alias="水位")]

    model_config = {
        "populate_by_name": True,  # 支持英文字段名或别名
        "json_schema_extra": {
            "examples": [
                {"system": "西甲95"},
                {"interval": "0区"},
                {"h": 1.38},
                {"d": 4.4},
                {"a": 8.0},
                {"return_rate": 94.5},
                {"goal_line": -1.25},
                {"water_level": "低"},
            ]
        },
    }

    @property
    def markdown_text(self):
        return f"{self.system} | {self.interval} | {self.h} | {self.d} | {self.a} | {self.return_rate} | {self.goal_line} | {self.water_level} |"

    @model_validator(mode="before")
    @classmethod
    def model_validate(cls, values: dict):
        # 把别名填充到英文字段名
        for k, v in cls._alias_map().items():
            if k in values and v not in values:
                values[v] = values[k]
                del values[k]

        # 校验字段是否缺失
        for field in cls._required_fields():
            if field not in values:
                raise ValueError(f"❌ 缺少 {field} 的值")

        values["system"] = values["system"].replace("体系", "")

        # 数值字段转换
        for field in ["h", "d", "a", "return_rate", "goal_line"]:
            try:
                float_value = float(values[field])
                float_value = 0.0 if float_value == 0.0 else float_value
                values[field] = float_value
            except (TypeError, ValueError):
                raise ValueError(f"❌ 字段 {field} 必须是数字，当前值: {values[field]}")

        if values["h"] < 1.0:
            raise ValueError("❌ 欧指-主胜赔率(H)不能小于1.0")
        if values["d"] < 1.0:
            raise ValueError("❌ 欧指-平局赔率(D)不能小于1.0")
        if values["a"] < 1.0:
            raise ValueError("❌ 欧指-客胜赔率(A)不能小于1.0")
        if values["return_rate"] < 0 or values["return_rate"] > 100:
            raise ValueError("❌ 返还率(%)必须在0到100之间")
        return values

    @classmethod
    def _alias_map(cls):
        return {
            "体系": "system",
            "区间": "interval",
            "胜": "h",
            "平": "d",
            "负": "a",
            "返还率": "return_rate",
            "让球盘口": "goal_line",
            "水位": "water_level",
        }

    @classmethod
    def _required_fields(cls):
        return [
            "system",
            "interval",
            "h",
            "d",
            "a",
            "return_rate",
            "goal_line",
            "water_level",
        ]


class HYREuroOddsRange(BaseModel):
    """生成胜负平赔率范围模型"""

    low_h: Annotated[float, Field(..., description="主胜赔率(H) 低位")]
    hight_h: Annotated[float, Field(..., description="主胜赔率(H) 高位")]
    low_d: Annotated[float, Field(..., description="平局赔率(D) 低位")]
    hight_d: Annotated[float, Field(..., description="平局赔率(D) 高位")]
    low_a: Annotated[float, Field(..., description="客胜赔率(A) 低位")]
    hight_a: Annotated[float, Field(..., description="客胜赔率(A) 高位")]
    hight_h: Annotated[float, Field(..., description="主胜赔率(H) 高位")]
