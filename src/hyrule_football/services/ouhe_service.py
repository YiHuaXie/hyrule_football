import requests
from bs4 import BeautifulSoup
import re
from hyrule_football.models import MatchInfo
from hyrule_football.store import HotMatchStore
from hyrule_football.utils import get_logger
from typing import List

logger = get_logger(__name__)


def get_hot_match_list() -> List[MatchInfo]:
    store = HotMatchStore()
    matches = store.list_matches()
    if not matches:
        matches = request_hot_match_list()
    return matches


def request_hot_match_list() -> List[MatchInfo]:
    try:
        url = "http://ouhe.aiball365.com/"
        response = requests.get(url, proxies={"http": None}, timeout=5)
        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        # 提取比赛主客队
        spans = soup.find_all("span")

        start = None
        for i, s in enumerate(spans):
            if s.get_text(strip=True) == "热门赛事":
                start = i
                break

        end = len(spans)
        for i, s in enumerate(spans[start + 1 :], start + 1):
            if s.get_text(strip=True) == "热门排行":
                end = i
                break
        # 从热门赛事和热门排行中间提取比赛
        section = spans[start + 1 : end]

        teams = []
        for i, span in enumerate(section):
            if span.get_text(strip=True).upper() == "VS" and 0 < i < len(section) - 1:
                home = section[i - 1].get_text(strip=True)
                away = section[i + 1].get_text(strip=True)
                teams.append((home, away))

        # 2.提取比赛的id
        # html 的超链接规则:
        # + class 中包含 hotmatch-detail-item 字段
        # + href 中包含  /match?id=任意字符&amp;i=任意字符
        # + 经过 soup 解析的正则需要改为: /match?id=任意字符&i=任意字符
        class_pattern = re.compile(r".*\bhotmatch-detail-item\b.*")
        href_pattern = re.compile(r"/match\?id=([^&]+)&i=([^&]+)")

        match_ids = []

        for a_tag in soup.find_all("a", href=True, class_=class_pattern):
            href = a_tag["href"]
            match = href_pattern.search(href)
            if match:
                matchid = match.group(1)
                if matchid not in match_ids:
                    match_ids.append(matchid)

        # 3. 组装比赛信息
        match_list = []
        for match_id, (home, away) in zip(match_ids, teams):
            match_list.append(MatchInfo(home=home, away=away, match_id=match_id))

        logger.info(f"✅ hot match list: {match_list}")

        # 4.保存到缓存
        store = HotMatchStore()
        store.save_matches(match_list)

        return match_list
    except requests.exceptions.Timeout:
        logger.error("❌ 请求超时")
        return []
