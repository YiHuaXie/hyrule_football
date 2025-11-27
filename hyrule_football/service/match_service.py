from typing import List
from hyrule_football.schema import MatchInfo
from hyrule_football.store import get_match_store
from hyrule_football.utils import get_logger

from .api_service import request_hot_match_list as _request_hot_match_list
from .api_service import request_all_match_list as _request_all_match_list

logger = get_logger(__name__)


def get_match_for_name(match_name: str) -> List[MatchInfo]:
    team_list = match_name.upper().split("VS")
    if len(team_list) == 2:
        team_a = team_list[0].strip()
        team_b = team_list[1].strip()
    else:
        team_a = None
        team_b = None

    matches = get_match_store().list_matches()
    if not matches:
        matches = request_all_match_list()

    match_list = []
    for a_match in matches:
        match_desc = a_match.match_description
        condition_1 = team_a and team_b and (team_a in match_desc and team_b in match_desc)
        condition_2 = match_name in match_desc
        if condition_1 or condition_2:
            match_list.append(a_match)

    return match_list


def request_hot_match_list() -> List[MatchInfo]:
    return [MatchInfo(**m) for m in _request_hot_match_list()]


def request_all_match_list():
    match_list = _request_all_match_list()
    matches = [MatchInfo(**m) for m in match_list]
    store = get_match_store()
    store.clear_all()
    store.save_matches(matches)
    return matches
