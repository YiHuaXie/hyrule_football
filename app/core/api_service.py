import requests
from bs4 import BeautifulSoup
import json
from typing import List
import os
from app.utils import get_logger
from app.clients import HTTPClient

logger = get_logger(__name__)

default_headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Encoding": "gzip, deflate",
    "Content-Type": "application/json",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Origin": os.getenv("OUHE_HTML_URL"),
    "Host": os.getenv("OUHE_API_HOST"),
}

client = HTTPClient(
    base_url=os.getenv("OUHE_API_URL"),
    timeout=10,
    headers=default_headers,
)


def request_hot_match_list() -> List[dict]:
    try:
        url = os.getenv("OUHE_HTML_URL")
        response = requests.get(url, proxies={"http": None}, timeout=5)
        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        script_tag = soup.find("script", id="__NEXT_DATA__", type="application/json")
        json_object = json.loads(script_tag.get_text())
        match_list = json_object["props"]["pageProps"]["data"]["hotMatchList"]

        return match_list
    except Exception as e:
        logger.error(f"❌ 获取热门赛事失败：{e}")
        return []


def request_all_match_list():
    try:
        res = client.post(
            "/web/matchLiveList",
            json={
                "channel": "web",
                "os": "browser",
                "matchType": 1,
                "page": 0,
                "size": 10000,
                "type": 1,
            },
        )

        match_list = res["data"]["list"]
        logger.info(f"✅ 获取所有赛事成功：{match_list}")
        return match_list
    except Exception as e:
        logger.error(f"❌ 获取所有赛事失败：{e}")
        return []


def request_euro_odds_detail(match_id: str) -> dict:
    try:
        params = {"channel": "web", "os": "browser", "matchId": match_id}
        euro_res = client.post(path="/web/euroOdds", json=params)
        euro_detail = euro_res["data"]
        return euro_detail
    except Exception as e:
        logger.error(f"❌ 获取欧指数据失败：{e}")
        return {}


def request_asisa_odds_detail(match_id: str) -> dict:
    try:
        params = {"channel": "web", "os": "browser", "matchId": match_id}
        asia_res = client.post(path="/web/asiaOdds", json=params)
        asia_detail = asia_res["data"]
        return asia_detail
    except Exception as e:
        logger.error(f"❌ 获取亚盘数据失败：{e}")
        return {}


def request_euro_odds_list(match_id: str) -> List[dict]:
    detail = request_euro_odds_detail(match_id)
    return detail.get("oddsList", [])


def request_asia_odds_list(match_id: str) -> List[dict]:
    detail = request_asisa_odds_detail(match_id)
    return detail.get("oddsList", [])


def request_league_list() -> List[dict]:
    """获取联赛列表"""
    try:
        url = os.getenv("OUHE_HTML_URL") + "league-center"
        response = requests.get(url, proxies={"http": None}, timeout=5)
        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        script_tag = soup.find("script", id="__NEXT_DATA__", type="application/json")
        json_object = json.loads(script_tag.get_text())
        league_list = json_object["props"]["pageProps"]["data"]

        return league_list
    except Exception as e:
        logger.error(f"❌ 获取联赛列表失败：{e}")
        return []


def request_league_round_match_list() -> List[dict]:
    """获取联赛轮次的比赛列表"""
    pass
