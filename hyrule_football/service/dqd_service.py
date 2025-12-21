import requests
import json
from bs4 import BeautifulSoup
import execjs
from urllib.parse import urljoin
from typing import Any, Optional, List
from hyrule_football.utils import get_logger
import json
import httpx


logger = get_logger(__name__)

DONG_QIU_DI_URL = "https://www.dongqiudi.com"

# DONG_QIU_DI_URL = "https://sport-data-magicball.dongdianqiu.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/142.0.0.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": DONG_QIU_DI_URL,
}

APP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/142.0.0.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9",
}


def _execute_js_iife(js_code: str) -> dict:
    """执行 JS IIFE 并返回结果"""
    wrapped_code = f"var result = {js_code};"
    # 使用 execjs 执行
    ctx = execjs.compile(wrapped_code)
    return ctx.eval("result")


def _request_page_data(path: str) -> dict | list | None:
    try:
        response = requests.get(urljoin(DONG_QIU_DI_URL, path), timeout=5, headers=HEADERS)
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


def request_league_data() -> List[dict]:
    """请求懂球帝的联赛列表"""
    data = _request_page_data("data")
    return data.get("tabList", []) if isinstance(data, dict) else []


def request_match_analysis(match_id: str) -> dict:
    """请求懂球帝的比赛详情"""
    data = _request_page_data(f"liveDetail/{match_id}")
    return data.get("analysisInitData", {}) if isinstance(data, dict) else {}


def request_team_detail(team_id: str) -> dict:
    """请求懂球帝的球队详情"""
    data = _request_page_data(f"team/{team_id}")
    return data if isinstance(data, dict) else {}


def request_daily_match_list():

    result = httpx.get(
        "https://sport-data-magicball.dongdianqiu.com/v1/list/match_list?isTeenager=0&platform=ios&theme=dark&language=zh-CN&version=845&timezone=GMT%2B8&cmp_type=soccer&tab_type=all"
    )
    return result.json().get("data", {}).get("matches", [])


# https://sport-data-magicball.dongdianqiu.com/v1/list/match_list?isTeenager=0&platform=ios&theme=dark&language=zh-CN&version=845&timezone=GMT%2B8&cmp_type=soccer&tab_type=all
