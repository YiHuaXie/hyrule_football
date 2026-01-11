from pydantic import BaseModel, Field


class CompanySchema(BaseModel):
    cid: int = Field(..., description="博彩公司ID", alias="id")
    cname: str = Field(..., description="博彩公司名称", alias="name")

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }
