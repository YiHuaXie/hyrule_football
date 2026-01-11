import requests
import httpx

from bs4 import BeautifulSoup
import json
from typing import List, Optional
from hyrule_football.utils import get_logger, deep_get, error_msg
from functools import wraps
from urllib.parse import urlparse, urljoin

OUHE_API_URL = "http://backend.aiball365.com"
OUHE_HTML_URL = "http://ouhe.aiball365.com"

_common_headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Encoding": "gzip, deflate",
    "Content-Type": "application/json",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Origin": OUHE_HTML_URL,
    "Host": urlparse(OUHE_API_URL).hostname,
}

_common_params = {"channel": "web", "os": "browser"}

logger = get_logger(__name__)


def _try_request(httpx_fn):
    try:
        response = httpx_fn()  # 执行外部传入的请求动作
        response.raise_for_status()
        return response.json()

    except httpx.TimeoutException as e:
        print("❌ 请求超时")
        raise e

    except httpx.ConnectError as e:
        print("❌ 连接错误")
        raise e

    except httpx.HTTPStatusError as e:
        print(f"❌ 请求失败, status: {e.response.status_code}, text: {e.response.text}")
        raise e

    except httpx.RequestError as e:
        print(f"❌ 请求错误, reason: {e}")
        raise e

    except Exception as e:
        print(f"❌ 其他错误: {e}")
        raise e


def _with_common_headers_params(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # ----- 合并 headers -----
        user_headers = kwargs.get("headers") or {}
        merged_headers = {**_common_headers, **user_headers}
        kwargs["headers"] = merged_headers

        # ----- 合并 params -----
        user_params = kwargs.get("params") or {}
        merged_params = {**_common_params, **user_params}
        kwargs["params"] = merged_params

        return func(*args, **kwargs)

    return wrapper


@_with_common_headers_params
def _get_request(path: str, headers: dict = None, params: dict = None):
    url = urljoin(OUHE_API_URL, path)
    logger.info(f"GET {url}, params={params}")
    return _try_request(lambda: httpx.get(url, headers=headers, params=params))


@_with_common_headers_params
def _post_request(path: str, headers: dict = None, params: dict = None):
    try:
        url = urljoin(OUHE_API_URL, path)
        logger.info(f"POST {url}, params={params}")
        return _try_request(lambda: httpx.post(url, headers=headers, json=params))
    except Exception as e:
        logger.error(error_msg("_post_request", e, data=url))
        return {}


def _request_page_props(path: str) -> Optional[dict]:
    try:
        final_url = urljoin(OUHE_HTML_URL, path)
        logger.info(f"Get HTML Text: {final_url}")
        response = requests.get(final_url, proxies={"http": None}, timeout=5)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        script_tag = soup.find("script", id="__NEXT_DATA__", type="application/json")
        next_data = json.loads(script_tag.get_text())

        page_props = deep_get(next_data, ["props", "pageProps"], None)
        return page_props
    except Exception as e:
        logger.error(error_msg("_request_page_props", e, data=final_url))
        return None


def request_league_list() -> List[dict]:
    """获取联赛列表"""
    page_props = _request_page_props("league-center")
    continent_groups = page_props.get("data", [])
    all_leagues = []
    for continent_group in continent_groups:
        league_list = continent_group.get("leagueList", [])
        all_leagues.extend(league_list)

    return list({x["leagueId"]: x for x in all_leagues}.values())


def request_league_detail(league_id: int) -> dict:
    """联赛详情"""
    page_props = _request_page_props(f"league-center/detail?leagueId={league_id}")
    return page_props or {}


def request_league_summary(league_id: int, season: str) -> dict:
    """联赛赛季数据"""
    params = {"leagueId": league_id, "season": season}
    response = _post_request("web/leagueSummaryWeb", params=params)
    return response.get("data", {})


def request_league_match_score(league_id: int, sub_league_id: int, season: str) -> dict:
    """联赛赛季子模块数据"""
    params = {"leagueId": league_id, "subLeagueId": sub_league_id, "season": season}
    response = _post_request("web/leagueMatchScoreWeb", params=params)
    return response.get("data", {})


# def request_teams_by_league(league_id: int):

#     def first_step():
#         page_props = _request_page_props(f"league-center/detail?leagueId={league_id}")
#         total_rank = deep_get(page_props, ["leagueScore", "totalRank"])
#         return total_rank, page_props

#     def second_step(page_props):
#         current_season = deep_get(page_props, ["data", "season"])
#         season_list = deep_get(page_props, ["seasonList"])
#         if not season_list:
#             season_list = deep_get(page_props, ["data", "seasonList"])
#         season_list = [season for season in season_list if season != current_season]
#         if not season_list:
#             return [], {}
#         last_season = season_list[0]
#         # 尝试获取上个赛季的数据
#         league_summary = request_league_summary(league_id, last_season)
#         return_league_id = deep_get(league_summary, ["summary", "leagueId"])
#         if return_league_id != league_id:
#             return [], {}

#         total_rank = deep_get(league_summary, ["matchScore", "totalRank"])
#         if total_rank:
#             return total_rank, {}

#         return [], league_summary

#     def third_step(league_summary):
#         sub_arr = deep_get(league_summary, ["schedule", "footballLeagueSubArr"], [])
#         if not sub_arr:
#             return []

#         target = next((x for x in sub_arr if x.get("footballLeagueSubName") == "联赛"), None)
#         sub_league_id = target.get("footballLeagueSubId")
#         if not sub_league_id:
#             return []

#         season = deep_get(league_summary, ["summary", "season"])
#         response = request_league_match_score_data(league_id, sub_league_id, season)
#         print(f"response: {response}")
#         return response.get("totalRank", [])

#     total_rank, page_props = first_step()
#     if not total_rank:
#         total_rank, league_summary = second_step(page_props)
#     if not total_rank:
#         total_rank = third_step(league_summary)
#     if not total_rank:
#         return []

#     team_list = total_rank[0].get("list", [])
#     return team_list


def request_league_match_round(league_id: int, sub_league_id: int, season: str, round: str) -> dict:
    params = {
        "leagueId": league_id,
        "subLeagueId": sub_league_id,
        "round": round,
        "season": season,
    }

    response = _post_request("web/leagueMatchRoundWeb", params=params)
    return response.get("data", {})


def request_match_list(
    leagues: Optional[List[int]], match_type: int = 0, type: int = 1
) -> List[dict]:
    """
    请求赛事列表
        Args:
            leagues: 联赛ID列表
            match_type: 赛事类型 0: 全部 1: 竞足 2: 北单 3: 十四场
            type: 赛事状态 1: 即时 2: 已完赛
    """

    try:
        params = {
            "matchType": match_type,
            "page": 0,
            "size": 10000,
            "type": type,
            "leagues": leagues,
        }
        res = _post_request("web/matchLiveList", params=params)
        return deep_get(res, ["data", "list"], default=[])
    except Exception as e:
        logger.error(f"❌ request_match_list 失败：{e}")
        return []


def request_daily_match_list():
    try:
        params = {"matchType": 1, "page": 0, "size": 10000, "type": 1}
        res = _post_request("web/matchLiveList", params=params)
        return deep_get(res, ["data", "list"], default=[])
    except Exception as e:
        logger.error(f"❌ 获取所有赛事失败：{e}")
        return []


def request_euro_odds_detail(match_id: str) -> dict:
    try:
        params = {"matchId": match_id}
        euro_res = _post_request("web/euroOdds", params=params)
        return euro_res.get("data", {})
    except Exception as e:
        logger.error(f"❌ 获取欧指数据失败：{e}")
        return {}


def request_asia_odds_detail(match_id: str) -> dict:
    try:
        params = {"matchId": match_id}
        asia_res = _post_request("web/asiaOdds", params=params)
        return asia_res.get("data", {})
    except Exception as e:
        logger.error(f"❌ 获取亚盘数据失败：{e}")
        return {}


def request_match_detail(match_id: str) -> dict:
    """获取比赛详情"""
    try:
        page_props = _request_page_props(f"match?id={match_id}&i=0")
        match_detail = page_props.get("data", {})
        # match_detail = _request_page_data(f"match?id={match_id}&i=0") or {}
        return match_detail
    except Exception as e:
        logger.error(f"❌ 获取亚盘数据失败：{e}")
        return {}


def request_match_analysis(match_id: str) -> dict:
    try:
        params = {"matchId": match_id}
        res = _post_request("web/clashAnalysisWeb", params=params)
        return res.get("data", {})
    except Exception as e:
        logger.error(f"❌ 获取对阵分析失败：{e}")
        return {}
