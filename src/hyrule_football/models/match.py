from pydantic import BaseModel, Field
from typing_extensions import Annotated


class MatchInfo(BaseModel):
    """生成赛事信息模型"""

    home: Annotated[str, Field(..., description="主队")]
    away: Annotated[str, Field(..., description="客队")]
    match_id: Annotated[str, Field(..., description="比赛ID")]

    @property
    def match_description(self) -> str:
        return f"{self.home}(主) VS {self.away}(客)"
