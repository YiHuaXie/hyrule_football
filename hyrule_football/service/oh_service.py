import requests
from bs4 import BeautifulSoup
import json
from typing import List
from hyrule_football.utils import get_logger
import httpx
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
        logger.error("❌ 请求超时")
        raise e

    except httpx.ConnectError as e:
        logger.error("❌ 连接错误")
        raise e

    except httpx.HTTPStatusError as e:
        logger.error(f"❌ 请求失败, status: {e.response.status_code}, text: {e.response.text}")
        raise e

    except httpx.RequestError as e:
        logger.error(f"❌ 请求错误, reason: {e}")
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
    url = urljoin(OUHE_API_URL, path)
    logger.info(f"POST {url}, params={params}")
    return _try_request(lambda: httpx.post(url, headers=headers, json=params))


def _request_page_data(path: str) -> dict | None | list:
    try:
        response = requests.get(urljoin(OUHE_HTML_URL, path), proxies={"http": None}, timeout=5)
        response.raise_for_status()
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        script_tag = soup.find("script", id="__NEXT_DATA__", type="application/json")
        page_data = _deep_get(
            json.loads(script_tag.get_text()),
            ["props", "pageProps", "data"],
            default=None,
        )
        return page_data
    except Exception as e:
        logger.error(f"❌ 获取欧核页面数据失败：{e}")
        return None


def _deep_get(d, keys, default=None):
    for key in keys:
        if isinstance(d, dict):
            d = d.get(key, default)
        else:
            return default
    return d


def request_hot_match_list() -> List[dict]:
    try:
        page_data = _request_page_data("/")
        match_list = page_data.get("hotMatchList", [])
        return match_list
    except Exception as e:
        logger.error(f"❌ 获取热门赛事失败：{e}")
        return []


def request_daily_match_list():
    try:
        params = {"matchType": 1, "page": 0, "size": 10000, "type": 1}
        res = _post_request("web/matchLiveList", params=params)
        return _deep_get(res, ["data", "list"], default=[])
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


def request_league_data() -> List[dict]:
    """获取联赛列表（展开所有大洲的联赛）"""
    try:
        continent_groups = _request_page_data("league-center") or []
        print(continent_groups)
        # 展开所有大洲的联赛列表
        all_leagues = []
        for continent_group in continent_groups:
            league_list = continent_group.get("leagueList", [])
            all_leagues.extend(league_list)

        return all_leagues
    except Exception as e:
        logger.error(f"❌ 获取联赛列表失败：{e}")
        return []


def request_league_detail(league_id: str) -> dict:
    try:
        continent_groups = _request_page_data("league-center") or []
        print(continent_groups)
        # 展开所有大洲的联赛列表
        all_leagues = []
        for continent_group in continent_groups:
            league_list = continent_group.get("leagueList", [])
            all_leagues.extend(league_list)

        return all_leagues
    except Exception as e:
        logger.error(f"❌ 获取联赛列表失败：{e}")
        return []

    _request_page_data(f"league-center/detail?leagueId={league_id}")


def request_match_detail(match_id: str) -> dict:
    """获取比赛详情"""
    try:
        match_detail = _request_page_data(f"match?id={match_id}&i=0") or {}
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
