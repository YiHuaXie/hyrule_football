import requests
from bs4 import BeautifulSoup
import json
from typing import List
import os
from hyrule_football.utils import get_logger
from hyrule_football.config import settings
import httpx
from functools import wraps
from urllib.parse import urlparse, urljoin

_common_headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Encoding": "gzip, deflate",
    "Content-Type": "application/json",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Origin": settings.OUHE_HTML_URL,
    "Host": urlparse(settings.OUHE_API_URL).hostname,
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
    url = urljoin(settings.OUHE_API_URL, path)
    logger.info(f"GET {url}, params={params}")
    return _try_request(lambda: httpx.get(url, headers=headers, params=params))


@_with_common_headers_params
def _post_request(path: str, headers: dict = None, params: dict = None):
    url = urljoin(settings.OUHE_API_URL, path)
    logger.info(f"POST {url}, params={params}")
    return _try_request(lambda: httpx.post(url, headers=headers, json=params))


def _request_html_text(url: str) -> str:
    try:
        response = requests.get(url, proxies={"http": None}, timeout=5)
        response.raise_for_status()
        html = response.text
        return html
    except Exception as e:
        logger.error(f"❌ 获取 HTML 失败：{e}")
        return ""


def _deep_get(d, keys, default=None):
    for key in keys:
        if isinstance(d, dict):
            d = d.get(key, default)
        else:
            return default
    return d


def request_hot_match_list() -> List[dict]:
    try:
        html = _request_html_text(settings.OUHE_HTML_URL)
        soup = BeautifulSoup(html, "html.parser")
        script_tag = soup.find("script", id="__NEXT_DATA__", type="application/json")
        json_object = json.loads(script_tag.get_text())
        match_list = _deep_get(
            json_object,
            ["props", "pageProps", "data", "hotMatchList"],
            default=[],
        )

        return match_list
    except Exception as e:
        logger.error(f"❌ 获取热门赛事失败：{e}")
        return []


def request_all_match_list():
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


def request_league_list() -> List[dict]:
    """获取联赛列表"""
    try:
        html = _request_html_text(urljoin(settings.OUHE_HTML_URL, "league-center"))
        soup = BeautifulSoup(html, "html.parser")
        script_tag = soup.find("script", id="__NEXT_DATA__", type="application/json")
        json_object = json.loads(script_tag.get_text())
        return _deep_get(
            json_object,
            ["props", "pageProps", "data"],
            default=[],
        )
    except Exception as e:
        logger.error(f"❌ 获取联赛列表失败：{e}")
        return []
