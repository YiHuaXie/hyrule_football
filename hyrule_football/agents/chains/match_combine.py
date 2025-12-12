from hyrule_football.service import dqd_service as dqd
from hyrule_football.service import oh_service as oh
from pydantic import BaseModel, Field
from hyrule_football.schema.match_base import MatchInfo
from typing_extensions import Annotated
from typing import List
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_deepseek import ChatDeepSeek
from hyrule_football.config import settings
from datetime import datetime


def match_combine(match: MatchInfo, dqd_match_list: List[dict]):
    dt = datetime.strptime(match.match_time, "%Y-%m-%d %H:%M")
    date_key = dt.strftime("%Y-%m-%d")
    date_match_list = dqd_match_list.get(date_key, [])
    if not date_match_list:
        return match

    if match.dqd_match_id or match.home_dqd_team_id or match.away_dqd_team_id:
        return match

    pydantic_parser = PydanticOutputParser(pydantic_object=MatchInfo)
    llm = ChatDeepSeek(
        model=settings.DEEPSEEK_CHAT,
        api_key=settings.DEEPSEEK_API_KEY,
    )

    prompt = PromptTemplate(
        template="""
        从 assistant_match_list 中找到和 main_match 中 匹配的赛事信息，
        若存在匹配数据，将辅助数据源的赛事信息合并到主数据源的赛事信息中
        {format_instructions}
        main_match: {main}
        assistant_match_list: {assistant}
        """,
        input_variables=["main", "assistant"],
        partial_variables={
            "format_instructions": pydantic_parser.get_format_instructions(),
        },
    )

    chain = prompt | llm | pydantic_parser
    result = chain.invoke({"main": match, "assistant": date_match_list})
    return MatchInfo(**result)


def main():
    dqd_match_list = dqd.request_daily_match_list()

    oh_match_list = [MatchInfo(**m) for m in oh.request_daily_match_list()]
    oh_match = [m for m in oh_match_list if m.home == "曼彻斯特联" or m.away == "曼彻斯特联"]
    oh_match = oh_match[0]

    dt = datetime.strptime(oh_match.match_time, "%Y-%m-%d %H:%M")
    date_str = dt.strftime("%Y-%m-%d")

    oh_match = match_combine(oh_match, dqd_match_list)
    print(f"合并后数据：{oh_match}")


if __name__ == "__main__":
    main()

# def request_daily_match_list():


#     return match_list_combine(oh_match_list, dqd_match_list)

# def match_list_combine(main_match_list, assistant_match_list):
