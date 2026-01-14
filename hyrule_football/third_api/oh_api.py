import httpx
from bs4 import BeautifulSoup
import json
from typing import List, Optional, Dict, Tuple
from hyrule_football.utils import get_logger, deep_get, error_msg
from hyrule_football.third_api.httpx_utils import httpx_defaults, try_request, trace_httpx_request
from urllib.parse import urlparse, urljoin

API_URL = "http://backend.aiball365.com"
HTML_URL = "http://ouhe.aiball365.com"

API_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Encoding": "gzip, deflate",
    "Content-Type": "application/json",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Origin": HTML_URL,
    "Host": urlparse(API_URL).hostname,
}

API_PARAMS = {"channel": "web", "os": "browser"}

HTML_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Encoding": "gzip, deflate",
    "Content-Type": "application/json",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Host": urlparse(HTML_URL).hostname,
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

logger = get_logger(__name__)


@httpx_defaults(headers=API_HEADERS, params=API_PARAMS)
async def _post_request(path: str, headers: Optional[Dict] = None, params: Optional[Dict] = None):
    url = urljoin(API_URL, path)
    logger.info(f"POST {url}, params={params}")
    try:
        return await try_request(async_client.post(url, headers=headers, json=params))
    except Exception as e:
        logger.error(error_msg("_post_request", e, data=url))
        return None


async def _request_page_props(path: str) -> dict:
    final_url = urljoin(HTML_URL, path)
    try:
        response = await async_client.get(final_url, headers=HTML_HEADERS)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        script_tag = soup.find("script", id="__NEXT_DATA__", type="application/json")
        if not script_tag:
            raise ValueError("not found __NEXT_DATA__ tag")

        next_data = json.loads(script_tag.get_text())
        page_props = deep_get(next_data, ["props", "pageProps"], {})
        return page_props
    except Exception as e:
        logger.error(error_msg("_request_page_props", e, data=final_url))
        return {}


async def request_league_list() -> List[dict]:
    """获取联赛列表"""
    page_props = await _request_page_props("league-center")
    continent_groups = page_props.get("data", [])
    all_leagues = []
    for continent_group in continent_groups:
        league_list = continent_group.get("leagueList", [])
        all_leagues.extend(league_list)

    return list({x["leagueId"]: x for x in all_leagues}.values())


async def request_league_detail(league_id: int) -> dict:
    """联赛详情"""
    return await _request_page_props(f"league-center/detail?leagueId={league_id}")


async def request_league_summary(league_id: int, season: str) -> dict:
    """联赛赛季数据"""
    params = {"leagueId": league_id, "season": season}
    response = await _post_request("web/leagueSummaryWeb", params=params)
    return response.get("data") or {}


async def request_league_match_score(league_id: int, sub_league_id: int, season: str) -> dict:
    """联赛赛季子模块数据"""
    params = {"leagueId": league_id, "subLeagueId": sub_league_id, "season": season}
    response = await _post_request("web/leagueMatchScoreWeb", params=params)
    return response.get("data") or {}


async def request_league_match_round(league_id: int, sub_league_id: int, season: str, round: str) -> dict:
    params = {"leagueId": league_id, "subLeagueId": sub_league_id, "round": round, "season": season}
    response = await _post_request("web/leagueMatchRoundWeb", params=params)
    return response.get("data") or {}


async def teams_from_season(league_id: int, season: str) -> List[Dict]:
    """获取球队"""

    def teams_from_total_rank(total_rank: list) -> List[Dict]:
        if not isinstance(total_rank, list) or not total_rank:
            return []

        all_teams = []
        for rank in total_rank:
            team_list = rank.get("list", [])
            all_teams.extend(team_list)

        return all_teams

    async def teams_from_league_summary():
        summary = await request_league_summary(league_id, season)
        total_rank = deep_get(summary, ["matchScore", "totalRank"])
        return teams_from_total_rank(total_rank), summary

    async def teams_from_league_match_score(league_summary):
        sub_arr = deep_get(league_summary, ["schedule", "footballLeagueSubArr"], [])
        if not sub_arr:
            return []

        target = next((x for x in sub_arr if x.get("footballLeagueSubName") == "联赛"), {})
        sub_league_id = target.get("footballLeagueSubId")
        if not sub_league_id:
            return []

        response = await request_league_match_score(league_id, sub_league_id, season)
        total_rank = deep_get(response, ["totalRank"])
        return teams_from_total_rank(total_rank)

    try:
        teams, summary = await teams_from_league_summary()
        if teams:
            return teams
        return await teams_from_league_match_score(summary)
    except Exception as e:
        logger.error(error_msg("teams_from_season", e))
        return []


async def request_euro_odds_detail(match_id: str) -> dict:
    params = {"matchId": match_id}
    response = await _post_request("web/euroOdds", params=params)
    return response.get("data") or {}


async def request_asia_odds_detail(match_id: str) -> dict:
    params = {"matchId": match_id}
    response = await _post_request("web/asiaOdds", params=params)
    return response.get("data") or {}


async def main():
    # league_list = await request_league_list()
    # print(league_list)

    # res = await request_league_detail(31)
    # print(res)

    res = await request_league_summary(31, "2022-2023")
    print(res)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
