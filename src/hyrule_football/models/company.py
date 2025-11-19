from typing import Optional
from pydantic import BaseModel, Field
from typing_extensions import Annotated


class Company(BaseModel):
    """博彩公司模型"""

    cid: Annotated[int, Field(..., description="博彩公司ID")]
    name: Annotated[str, Field(..., description="博彩公司名称")]

    @classmethod
    def bet635(cls):
        return cls(cid=38, name="bet365")

    @classmethod
    def williamhill(cls):
        return cls(cid=26, name="威廉希尔")


_company_map = {
    "bet365": Company.bet635(),
    "威廉希尔": Company.williamhill(),
}

_company_name_map = {
    "bet365": "bet365",
    "365": "bet365",
    "williamhill": "威廉希尔",
    "威廉希尔": "威廉希尔",
    "威廉": "威廉希尔",
}


def get_company_by_name(name: str) -> Optional[Company]:
    """根据博彩公司名称获取 Company 对象"""

    name = name.lower()
    name = _company_name_map.get(name, name)

    return _company_map.get(name, None)
