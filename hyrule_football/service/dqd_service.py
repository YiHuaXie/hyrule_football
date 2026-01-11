import requests
from bs4 import BeautifulSoup
import execjs
from urllib.parse import urljoin
from typing import List
from hyrule_football.utils import get_logger, deep_get, error_msg
import httpx


logger = get_logger(__name__)

# 8647 是中国的苏超并不是苏格兰超
_DQD_LEAGUE_BLACK_LIST = ["8647"]
# DONG_QIU_DI_URL = "https://www.dongqiudi.com"

DQD_APP_MATCH_API_URL = "https://sport-data-magicball.dongdianqiu.com"
DQD_HTML_URL = "https://www.dongqiudi.com"
# DONG_QIU_DI_URL = "https://sport-data-magicball.dongdianqiu.com"

DQD_SPORT_DATA_API_BASE = "https://sport-data.dongqiudi.com/soccer/biz/data"


HTML_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/142.0.0.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": DQD_HTML_URL,
}

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


def _execute_js_iife(js_code: str) -> dict:
    """执行 JS IIFE 并返回结果"""
    wrapped_code = f"var result = {js_code};"
    # 使用 execjs 执行
    ctx = execjs.compile(wrapped_code)
    return ctx.eval("result")


def _request_page_data(path: str) -> dict | list | None:
    try:
        final_url = urljoin(DQD_HTML_URL, path)
        logger.info(f"Get HTML Text: {final_url}")
        response = requests.get(final_url, timeout=5, headers=HTML_HEADERS)
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
        logger.exception(f"❌ 懂球帝请求页面数据失败, {e}")
        return None


def request_league_list() -> List[dict]:
    """联赛列表"""
    page_data = _request_page_data("data")
    if not isinstance(page_data, dict):
        return []

    result = {}
    for x in page_data.get("tabList", []):
        cid = x.get("competition_id")
        # 去重并过滤黑名单
        if not cid or cid in _DQD_LEAGUE_BLACK_LIST:
            continue
        result[cid] = x

    return list(result.values())


def request_league_seasons(league_id: str) -> List[dict]:
    """联赛赛季列表"""
    try:
        params = {"app": "dqd", "language": "zh-cn", "competition_id": league_id}
        response = httpx.get(f"{DQD_SPORT_DATA_API_BASE}/seasons", params=params)
        response.raise_for_status()
        seasons = response.json() or []

        return [
            {
                "id": s.get("season_id"),
                "name": s.get("season_name"),
            }
            for s in seasons
            if s.get("season_id") and s.get("season_name")
        ]
    except Exception as e:
        logger.error(error_msg("request_league_seasons", e))
        return []


def request_team_points_rank_by_season(season_id: str) -> dict:
    """球队积分榜"""
    try:
        params = {"app": "dqd", "lang": "zh-cn", "season_id": season_id}
        response = httpx.get(f"{DQD_SPORT_DATA_API_BASE}/standing", params=params)
        response.raise_for_status()
        return response.json() or {}
    except Exception as e:
        logger.error(error_msg("request_team_points_rank_by_season", e))
        return []


def request_match_analysis(match_id: str) -> dict:
    """请求懂球帝的比赛详情"""
    data = _request_page_data(f"liveDetail/{match_id}")
    return data.get("analysisInitData", {}) if isinstance(data, dict) else {}


def request_team_detail(team_id: str) -> dict:
    """请求懂球帝的球队详情"""
    data = _request_page_data(f"team/{team_id}")
    return data if isinstance(data, dict) else {}


def request_daily_match_list() -> List[dict]:
    # https://sport-data.dongdianqiu.com
    result = httpx.get(
        "https://sport-data-magicball.dongdianqiu.com/v1/list/match_list?isTeenager=0&platform=ios&theme=dark&language=zh-CN&version=845&timezone=GMT%2B8&cmp_type=soccer&tab_type=all"
    )
    return result.json().get("data", {}).get("matches", [])


def request_played_match_list(start_date: str) -> List[dict]:
    try:
        params = {
            "tab_type": "played",
            "start": start_date,
            **APP_COMMON_PARAMS,
        }
        response = httpx.get(f"{DQD_APP_MATCH_API_URL}/v1/list/schedule_list", params=params)
        response.raise_for_status()
        return deep_get(response.json(), ["data", "matches"], default=[])
    except Exception as e:
        logger.error(f"❌ 获取懂球帝完赛列表失败：{e}")
        return []


def request_test():
    print("test")
    result = httpx.get("https://api.dongdianqiu.com/data/index?app=dqd&version=846&platform=iphone&type=zuqiu")
    data = result.json()

    return data
    # import json

    # print(json.dumps(data, indent=4, ensure_ascii=False))


# request_test()


#  https://api.dongdianqiu.com/v3/archive/app/tabs/getlists?id=253&platform=iphone&version=846"
# "https://api.dongdianqiu.com/v3/archive/app/channel/feeds?type=team&id=50001042&version=846&platform=ios&isDarkMode=1&user_pay_type=8192&isView=0&device_type=ios&isTeenager=0&isDarkMode=1"
# https://sport-data-magicball.dongdianqiu.com/v1/list/match_list?isTeenager=0&platform=ios&theme=dark&language=zh-CN&version=845&timezone=GMT%2B8&cmp_type=soccer&tab_type=all
# 欧冠 24670
# 联赛积分榜：https://sport-data.dongqiudi.com/soccer/biz/data/standing?app=dqd&lang=zh-cn&season_id=24596
# 联赛赛程：https://sport-data.dongqiudi.com/soccer/biz/data/schedule?season_id=24596&app=dqd&language=zh-cn
# 联赛赛程基于轮数：https://sport-data.dongqiudi.com/soccer/biz/data/schedule?season_id=24596&round_id=432736&gameweek=1&app=dqd
# 联赛赛季列表：https://sport-data.dongqiudi.com/soccer/biz/data/seasons?competition_id=43&app=dqd&version=0&language=zh-cn
