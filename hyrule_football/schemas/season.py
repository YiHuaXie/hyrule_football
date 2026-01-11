from pydantic import BaseModel, model_validator, field_validator, model_serializer
from hyrule_football.utils import specific_season_name
from typing import List


class SeasonSchema(BaseModel):
    league: str = ""
    id: str = ""
    name: str = ""

    @field_validator("*", mode="before")
    def _covert_to_str(cls, v):
        if v is None:
            return ""
        try:
            return str(v)
        except ValueError:
            return ""

    @model_validator(mode="after")
    def _standardize_season(self):
        self.name = specific_season_name(self.league, self.name)
        return self

    # 仅保留 id 和 name
    # 当 SeasonSchema 嵌套的时候，重写 model_dump() 函数不生效
    @model_serializer(mode="plain")
    def serialize(self):
        return {"id": self.id, "name": self.name}

    # @classmethod
    # def schemas_from_names(cls, league: str, names: List[str]) -> List["SeasonSchema"]:
    #     if not isinstance(names, list) or not league:
    #         return []

    #     return [cls(league=league, id=n, name=n) for n in names if n]

    # @classmethod
    # def schemas_from_list(cls, league: str, data_list: List[dict]) -> List["SeasonSchema"]:
    #     if not isinstance(data_list, list) or not league:
    #         return []

    #     return [cls(league=league, **d) for d in data_list if isinstance(d, dict) and d.get("id") and d.get("name")]


if __name__ == "__main__":
    s = SeasonSchema(league="欧冠杯", id="24670", name="2025-2026")
    print(s.model_dump())
    s = SeasonSchema(league="英超", id=None, name="25/26")
    print(s.model_dump())
    s = SeasonSchema(league="欧洲杯", name="2019-2021")
    print(s.model_dump())
    s = SeasonSchema(league="欧洲杯", name="2023-2024")
    print(s.model_dump())
    s = SeasonSchema(league="欧洲杯", name="2024")
    print(s.model_dump())
    s = SeasonSchema(league="美职业", name="2026")
    print(s.model_dump())
