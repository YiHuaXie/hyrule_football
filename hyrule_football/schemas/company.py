from pydantic import BaseModel, Field, field_validator
from typing import List


class CompanyBase(BaseModel):
    cid: int = Field(..., description="博彩公司ID", alias="id")
    cname: str = Field(..., description="博彩公司名称", alias="name")

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }

    # @field_validator("cname", mode="before")
    # def standard_cname(cls, value: str) -> str:
    #     """标准化公司名称"""
    #     name_map = {
    #         "bet365": "Bet365",
    #         "365": "Bet365",
    #         "williamhill": "威廉希尔",
    #         "威廉希尔": "威廉希尔",
    #         "威廉": "威廉希尔",
    #     }
    #     return name_map.get(value.lower(), value)


class CompanyModel(BaseModel):
    cid: int = Field(..., description="博彩公司ID", alias="id")
    cname: str = Field(..., description="博彩公司名称", alias="name")

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }

    @classmethod
    def standard_name(cls, name: str) -> str:
        name_map = {
            "bet365": "Bet365",
            "365": "Bet365",
            "williamhill": "威廉希尔",
            "威廉希尔": "威廉希尔",
            "威廉": "威廉希尔",
        }
        return name_map.get(name.lower(), name)

    @field_validator("cname", mode="before")
    @classmethod
    def normalize_cname(cls, value: str) -> str:
        """标准化公司名称"""
        return cls.standard_name(value)


_all_company_list: List[CompanyModel] | None = None


def _get_all_company_list() -> List[CompanyModel]:
    global _all_company_list
    if _all_company_list is not None:
        return _all_company_list

    from pathlib import Path
    import json

    DATA_DIR = Path(__file__).parent.parent / "data"
    with open(DATA_DIR / "company.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        _all_company_list = [CompanyModel(**item) for item in data]

    return _all_company_list


all_company_list = _get_all_company_list()

default_company_list = [c for c in all_company_list if c.cname in ["Bet365", "威廉希尔"]]


def fixed_company_list(names: List[str]) -> List[CompanyModel]:
    company_list = all_company_list
    names = [CompanyModel.standard_name(name) for name in names]
    return [c for c in company_list if c.cname in names] or default_company_list


def test():
    """测试函数"""
    print(f"默认: {[c.cname for c in default_company_list]}")
    print(f"['365', '威廉']: {[c.cname for c in fixed_company_list(['365', '威廉'])]}")
    print(f"['bet365', '爱奇异']: {[c.cname for c in fixed_company_list(['bet365', '爱奇异'])]}")
    print(f"['爱奇异']: {[c.cname for c in fixed_company_list(['爱奇异'])]}")


if __name__ == "__main__":
    test()
