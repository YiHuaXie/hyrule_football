from pydantic import BaseModel, Field
from typing_extensions import Annotated


class Company(BaseModel):
    """博彩公司模型"""

    cid: Annotated[str, Field(..., description="博彩公司ID")]
    name: Annotated[str, Field(..., description="博彩公司名称")]

    @classmethod
    def bet635(cls):
        return cls(cid="38", name="bet365")

    @classmethod
    def williamhill(cls):
        return cls(cid="26", name="威廉希尔")
