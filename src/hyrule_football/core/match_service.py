import requests
from bs4 import BeautifulSoup
import json
from typing import List
import os

from hyrule_football.models import MatchInfo
from hyrule_football.store import get_match_store
from hyrule_football.utils import get_logger

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
        matches = request_hot_match_list()

    match_list = []
    for a_match in matches:
        match_desc = a_match.match_description
        condition_1 = team_a and team_b and (team_a in match_desc and team_b in match_desc)
        condition_2 = match_name in match_desc
        if condition_1 or condition_2:
            match_list.append(a_match)

    return match_list


def request_hot_match_list() -> List[MatchInfo]:
    try:
        url = os.getenv("OUHE_HTML_URL")
        response = requests.get(url, proxies={"http": None}, timeout=5)
        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        script_tag = soup.find("script", id="__NEXT_DATA__", type="application/json")
        json_object = json.loads(script_tag.get_text())
        match_list = json_object["props"]["pageProps"]["data"]["hotMatchList"]

        matches = [MatchInfo(**m) for m in match_list]

        store = get_match_store()
        store.clear_all()
        store.save_matches(matches)

        return matches
    except requests.exceptions.Timeout:
        logger.error("❌ 请求超时")
        return []
