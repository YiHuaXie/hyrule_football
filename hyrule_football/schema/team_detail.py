
from .match_base import MatchInfo
from pydantic import BaseModel, Field, model_validator, field_validator
from typing_extensions import Annotated
from typing import List

class TeamMember(BaseModel):
    """生成球队成员模型"""

    person_id: Annotated[str, Field(..., description="球员ID")]
    
    person_name: Annotated[str, Field(..., description="球员姓名")]
    
    title: Annotated[str, Field(..., description="球员位置")]

    

    
class TeamDetail(BaseModel):
    """生成赛事详细信息模型"""

    dqd_team_id: Annotated[str, Field(..., description="球队ID")]
    team_name: Annotated[str, Field(..., description="球队名称")]

    team_members: Annotated[List[TeamMember], Field(..., description="球队成员列表")]
    pass