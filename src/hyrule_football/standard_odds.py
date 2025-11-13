from pydantic import BaseModel, Field, model_validator
from typing_extensions import Annotated
from bs4 import BeautifulSoup
from markdown import markdown
from langchain_community.document_loaders import UnstructuredMarkdownLoader
import os
from typing import List


class StandardOdds(BaseModel):
    """生成欧洲指数（简称欧指）和亚洲盘口（简称亚盘）赔率对比模型"""

    system: Annotated[str, Field(..., description="体系名称", alias="体系")]
    interval: Annotated[str, Field(..., description="区间", alias="区间")]
    h: Annotated[float, Field(..., description="欧指-主胜赔率(H)", alias="胜")]
    d: Annotated[float, Field(..., description="欧指-平局赔率(D)", alias="平")]
    a: Annotated[float, Field(..., description="欧指-客胜赔率(A)", alias="负")]
    return_rate: Annotated[float, Field(..., description="返还率(%)", alias="返还率")]
    goal_line: Annotated[str, Field(..., description="亚盘-让球盘口", alias="让球盘口")]
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
                {"goal_line": "-1.25"},
                {"water_level": "低"},
            ]
        },
    }

    @model_validator(mode="before")
    @classmethod
    def model_validate(cls, values: dict):
        # 把别名填充到英文字段名
        for k, v in cls._alias_map().items():
            if k in values and v not in values:
                values[v] = values[k]

        # 校验字段是否缺失
        for field in cls._required_fields():
            if field not in values:
                raise ValueError(f"❌ 缺少 {field} 的值")

        # 数值字段转换
        for field in ["h", "d", "a", "return_rate"]:
            try:
                values[field] = float(values[field])
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


class HADOdds(BaseModel):
    """生成欧洲指数（简称欧指）赔率模型"""

    h: Annotated[float, Field(..., description="欧指-主胜赔率(H)")]
    d: Annotated[float, Field(..., description="欧指-平局赔率(D)")]
    a: Annotated[float, Field(..., description="欧指-客胜赔率(A)")]

    @classmethod
    def from_standard_odds(cls, odds: StandardOdds):
        return cls(h=odds.h, d=odds.d, a=odds.a)

    @classmethod
    def odds_list(cls, list: List[StandardOdds]):
        return [cls.from_standard_odds(odds) for odds in list]


class HADOddsRange(BaseModel):
    """生成欧洲指数（简称欧指）赔率范围模型"""

    low_h: Annotated[float, Field(..., description="欧指-主胜赔率(H) 低位")]
    hight_h: Annotated[float, Field(..., description="欧指-主胜赔率(H) 高位")]
    low_d: Annotated[float, Field(..., description="欧指-平局赔率(D) 低位")]
    hight_d: Annotated[float, Field(..., description="欧指-平局赔率(D) 高位")]
    low_a: Annotated[float, Field(..., description="欧指-客胜赔率(A) 低位")]
    hight_a: Annotated[float, Field(..., description="欧指-客胜赔率(A) 高位")]

    @classmethod
    def from_odds_list(cls, list: List[HADOdds] | List[StandardOdds]):
        h_list = [odds.h for odds in list]
        d_list = [odds.d for odds in list]
        a_list = [odds.a for odds in list]
        return cls(
            low_h=min(h_list),
            hight_h=max(h_list),
            low_d=min(d_list),
            hight_d=max(d_list),
            low_a=min(a_list),
            hight_a=max(a_list),
        )


def odds_serialization_from_markdown(markdown_path: str) -> list[StandardOdds]:
    """从 markdown 中解析赔率数据列表"""

    if not os.path.exists(markdown_path):
        raise FileNotFoundError(f"❌ 文件不存在: {markdown_path}")

    with open(markdown_path, "r", encoding="utf-8") as f:
        md_text = f.read().strip()
    
    html = markdown(md_text, extensions=["tables"])
     # 解析 HTML
    soup = BeautifulSoup(html, "lxml")
    rows = soup.find_all("tr")
    headers = [th.get_text(strip=True) for th in rows[0].find_all(["td", "th"])]
    # 解析数据行
    data_list = []
    for row in rows[1:]:
        values = [td.get_text(strip=True) for td in row.find_all("td")]
        # 转成 model
        row_dict = dict(zip(headers, values))
        odds_model = StandardOdds(**row_dict)
        data_list.append(odds_model)

    return data_list


def asia_filter_odds(
    odds_list: list[StandardOdds],
    system: str,
    goal_line: str,
    water_level: str,
) -> list[StandardOdds]:
    """通过亚盘过滤出符合条件的赔率数据"""
    result = []
    for odds in odds_list:
        if odds.system != system:
            continue
        if odds.water_level != water_level:
            continue
        if odds.goal_line != goal_line:
            continue
        result.append(odds)
    return result
