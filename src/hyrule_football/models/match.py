from pydantic import BaseModel, Field
from typing_extensions import Annotated

class MatchModel(BaseModel):
    """生成赛事模型"""

    home: Annotated[str, Field(..., description="主队")]
    away: Annotated[str, Field(..., description="客队")]
    match_id: Annotated[str, Field(..., description="比赛ID")]