import requests
from bs4 import BeautifulSoup
import execjs
from urllib.parse import urljoin
from typing import List, Optional, Dict
from hyrule_football.utils import get_logger, deep_get, error_msg
from hyrule_football.third_api.httpx_utils import httpx_defaults, try_request, trace_httpx_request
import httpx


logger = get_logger(__name__)

# 8647 是中国的苏超并不是苏格兰超
_LEAGUE_BLACK_LIST = {"8647"}


APP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/142.0.0.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

APP_COMMON_PARAMS = {
    "isTeenager": 0,
    "platform": "ios",
    "theme": "dark",
    "language": "zh-CN",
    "version": 845,
    "timezone": "GMT+8",
    "cmp_type": "soccer",
}


HTML_URL = "https://www.dongqiudi.com"
SPORT_DATA_API_URL = "https://sport-data.dongqiudi.com"
SPORT_DATA_MAGICBALL_API_URL = "https://sport-data-magicball.dongdianqiu.com"

HTML_COMMON_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0"
    "Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept": "text/html,application/xhtml+xml,application/xml;"
    "q=0.9,image/avif,image/webp,image/apng,*/*;"
    "q=0.8,application/signed-exchange;v=b3;q=0.7",
    # "Referer": HTML_URL,
}

SPORT_DATA_API_COMMON_PARAMS = {
    "app": "dqd",
    "lang": "zh-cn",
    "language": "zh-cn",
}

async_client = httpx.AsyncClient(
    timeout=httpx.Timeout(5.0),
    follow_redirects=False,
    limits=httpx.Limits(
        max_connections=10,
        max_keepalive_connections=5,
    ),
    event_hooks={
        "request": [trace_httpx_request],
    },
)


def _execute_js_iife(js_code: str) -> dict:
    # 执行 JS IIFE 并返回结果
    wrapped_code = f"var result = {js_code};"
    ctx = execjs.compile(wrapped_code)
    return ctx.eval("result")


async def _request_page_data(path: str):
    final_url = urljoin(HTML_URL, path)
    try:
        response = await async_client.get(final_url, headers=HTML_COMMON_HEADERS)
        response.raise_for_status()
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        # 获取包含 window.__NUXT__ 的 script 标签
        scripts = soup.find_all("script")
        script_texts = [s.get_text() for s in scripts]
        nuxt_script_text = next((s for s in script_texts if "window.__NUXT__" in s), None)

        if not nuxt_script_text:
            raise ValueError("未找到包含 window.__NUXT__ 的 script 标签")
        # 找到 IIFE 代码
        start = nuxt_script_text.find("(function")
        if start < 0:
            raise ValueError("未找到 IIFE 代码")

        # 提取 IIFE 代码并执行 js
        js_code = nuxt_script_text[start:]
        result = _execute_js_iife(js_code)
        data = result.get("data")

        return data[-1] if data else None
    except Exception as e:
        logger.error(error_msg("_request_page_data", e, data=final_url))
        return None


@httpx_defaults(headers=HTML_COMMON_HEADERS, params=SPORT_DATA_API_COMMON_PARAMS)
async def _sport_data_request(path: str, *, headers: dict = {}, params: dict = {}):
    final_url = f"{SPORT_DATA_API_URL}/soccer/biz/data/{path}"
    return await try_request(async_client.get(final_url, headers=headers, params=params))


# @httpx_defaults(headers=APP_HEADERS, params=APP_COMMON_PARAMS)
async def _sport_data_magicball_request(path: str, *, headers: dict = {}, params: dict = {}):
    pass


async def request_league_list() -> List[dict]:
    """联赛列表"""
    page_data = await _request_page_data("data")
    if not isinstance(page_data, dict):
        return []

    result = {}
    for x in page_data.get("tabList"):
        cid = x.get("competition_id")
        # 去重并过滤黑名单
        if not cid or cid in _LEAGUE_BLACK_LIST:
            continue
        result[cid] = x

    return list(result.values())


async def request_league_seasons(league_id: str) -> List[dict]:
    """联赛赛季列表"""

    params = {"competition_id": league_id}
    seasons = await _sport_data_request("seasons", params=params)
    seasons = seasons or []
    return [
        {"id": s.get("season_id"), "name": s.get("season_name")}
        for s in seasons
        if s.get("season_id") and s.get("season_name")
    ]


async def request_team_points_rank_by_season(season_id: str) -> dict:
    """赛季球队积分榜"""
    params = {"season_id": season_id}
    response = await _sport_data_request("standing", params=params)
    return response or {}


async def teams_from_season(season_id: str) -> List[dict]:
    try:
        response = await request_team_points_rank_by_season(season_id)
        rounds = deep_get(response, ["content", "rounds"])
        if not isinstance(rounds, list) or not rounds:
            return []

        REGULAR_KEY = "team_point_ranking_regular"
        GROUP_KEY = "team_point_ranking_group"
        all_teams = []
        for round_key in [REGULAR_KEY, GROUP_KEY]:
            matched_rounds = [r for r in rounds if r.get("template") == round_key]
            for matched_round in matched_rounds:
                data = deep_get(matched_round, ["content", "data"])
                if data and round_key == REGULAR_KEY:
                    all_teams.extend(data)
                elif data and round_key == GROUP_KEY:
                    for group in data:
                        all_teams.extend(group.get("data", []))

        return all_teams
    except Exception as e:
        logger.error(error_msg("teams_from_season", e))
        return []


async def main():
    # league_list = await request_league_list()
    # print(league_list)

    # seasons = await request_league_seasons("4")
    # print(seasons)

    res = await request_team_points_rank_by_season("24646")
    print(res)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
