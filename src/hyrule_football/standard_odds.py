from pydantic import BaseModel, Field, model_validator
from typing_extensions import Annotated


class StandardOdds(BaseModel):
    """生成欧洲指数（简称欧指）和亚洲盘口（简称亚盘）赔率对比模型"""

    system: Annotated[str, Field(..., description="体系名称")]
    interval: Annotated[str, Field(..., description="区间")]
    h: Annotated[float, Field(..., description="欧指-主胜赔率(H)")]
    d: Annotated[float, Field(..., description="欧指-平局赔率(D)")]
    a: Annotated[float, Field(..., description="欧指-客胜赔率(A)")]
    return_rate: Annotated[float, Field(..., description="返还率(%)")]
    goal_line: Annotated[str, Field(..., description="亚盘-让球盘口")]
    water_level: Annotated[str, Field(..., description="亚盘-水位（赔率）")]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"system": "西甲95"},
                {"interval": "0区"},
                {"h": 1.38},
                {"d": 4.4},
                {"a": 8.0},
                {"return_rate": 94.5},
                {"goal_line": "-1.25"},
                {"water_level": "低"},
            ]
        }
    }

    @model_validator(mode="before")
    @classmethod
    def model_validate(cls, values: dict):
        if "system" not in values:
            raise ValueError("❌ 缺少体系名称")
        if "interval" not in values:
            raise ValueError("❌ 缺少区间")
        if "h" not in values:
            raise ValueError("❌ 缺少欧指-主胜赔率(H)")
        if "d" not in values:
            raise ValueError("❌ 缺少欧指-平局赔率(D)")
        if "a" not in values:
            raise ValueError("❌ 缺少欧指-客胜赔率(A)")
        if "return_rate" not in values:
            raise ValueError("❌ 缺少返还率(%)")
        if "goal_line" not in values:
            raise ValueError("❌ 缺少亚盘-让球盘口")
        if "water_level" not in values:
            raise ValueError("❌ 缺少亚盘-水位（赔率）")

        if values["h"] < 1.0:
            raise ValueError("❌ 欧指-主胜赔率(H)不能小于1.0")
        if values["d"] < 1.0:
            raise ValueError("❌ 欧指-平局赔率(D)不能小于1.0")
        if values["a"] < 1.0:
            raise ValueError("❌ 欧指-客胜赔率(A)不能小于1.0")
        if values["return_rate"] < 0 or values["return_rate"] > 100:
            raise ValueError("❌ 返还率(%)必须在0到100之间")
        return values
