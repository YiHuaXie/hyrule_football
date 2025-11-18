from hyrule_football.services import match_service as _match_service
from langchain.tools import tool
from hyrule_football.utils import get_logger

logger = get_logger(__name__)


@tool
def get_match_list() -> str:
    """获取所有赛事或热门赛事"""

    logger.info(">>> [Tool] get_match_list 被调用")
    matches = _match_service.request_hot_match_list()
    match_list = [m.match_description for m in matches]
    if not match_list:
        return "当前没有找到赛事列表，请稍后再试"

    return "赛事列表：\n".join(match_list)


def get_match_for_name(team_name: str) -> str:
    """"""
    matches = _match_service.get_match_for_name(team_name)
    if not matches:
        return "没有找到相关比赛"
    if len(matches) > 1:
        return "找到多场比赛，请指定更具体的名字"
    if len(matches) == 1:
        return matches[0].match_description
