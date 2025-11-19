from hyrule_football.models import (
    MatchInfo,
    Company,
    BasedMatchOddsInfo,
    OddsSummary,
    Company,
    EuroOdds,
    AsiaOdds,
)
from hyrule_football.clients import HTTPClient
from hyrule_football.utils import get_logger, get_odds_system_name
from hyrule_football.core.odds_engine import OddsEngine

from typing import List
import os

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


def get_odds_for_match(
    match_info: MatchInfo,
    company_list: List[Company] = [Company.bet635(), Company.williamhill()],
    need_history: bool = False,
) -> BasedMatchOddsInfo:
    """获取某场比赛的赔率数据"""

    try:
        params = {"channel": "web", "os": "browser", "matchId": match_info.match_id}
        euro_res = client.post(path="/web/euroOdds", json=params)
        euro_odds_list = euro_res["data"]["oddsList"]
        asia_res = client.post(path="/web/asiaOdds", json=params)
        asia_odds_list = asia_res["data"]["oddsList"]

    except Exception as e:
        logger.error(f"❌ 获取欧赔数据失败：{e}")
        return BasedMatchOddsInfo(match_info=match_info)

    if not euro_odds_list and not asia_odds_list:
        return BasedMatchOddsInfo(match_info=match_info)

    odds_info = BasedMatchOddsInfo(
        match_info=match_info,
        company_list=company_list,
    )

    for company in company_list:
        home_odds_summary = OddsSummary(company=company, team_name=match_info.home)
        away_odds_summary = OddsSummary(company=company, team_name=match_info.away)

        # 生成欧指数据
        _gen_euro_odds(company.cid, euro_odds_list, home_odds_summary, away_odds_summary)
        # 生成亚盘数据
        _gen_asia_odds(company.cid, asia_odds_list, home_odds_summary, away_odds_summary)

        _gen_pattern(home_odds_summary, match_info.league)
        _gen_pattern(away_odds_summary, match_info.league)

        odds_info.home_summary_list.append(home_odds_summary)
        odds_info.away_summary_list.append(away_odds_summary)

    return odds_info


def _gen_pattern(summary: OddsSummary, match_league: str) -> None:
    """生成格局数据"""
    if summary.init_euro and summary.init_asia:
        init_euro = summary.init_euro
        init_system_name = get_odds_system_name(match_league, init_euro.return_rate)
        engine = OddsEngine(init_system_name)
        init_pattern = engine.euro_odds_pattern(summary.init_euro, summary.init_asia)
        if init_pattern:
            summary.init_pattern = f"{init_pattern[0]}-{init_pattern[1]}-{init_pattern[2]}"

    if summary.now_euro and summary.now_asia:
        now_euro = summary.now_euro
        now_system_name = get_odds_system_name(match_league, now_euro.return_rate)
        engine = OddsEngine(now_system_name)
        now_pattern = engine.euro_odds_pattern(summary.now_euro, summary.now_asia)
        if now_pattern:
            summary.init_pattern = f"{init_pattern[0]}-{init_pattern[1]}-{init_pattern[2]}"


def _gen_euro_odds(
    cid: str,
    euro_odds_list: list,
    home_odds_summary: OddsSummary,
    away_odds_summary: OddsSummary,
) -> None:
    odds = next((o for o in euro_odds_list if cid == o["cid"]), None)
    if not odds:
        return

    home_init_euro = EuroOdds(
        w=odds["initOddsWin"],
        d=odds["initOddsDraw"],
        l=odds["initOddsLose"],
        return_rate=odds["initReturnRates"],
    )
    home_now_euro = EuroOdds(
        w=odds["nowOddsWin"],
        d=odds["nowOddsDraw"],
        l=odds["nowOddsLose"],
        return_rate=odds["nowReturnRates"],
    )
    home_odds_summary.init_euro = home_init_euro
    home_odds_summary.now_euro = home_now_euro

    away_init_euro = home_init_euro.opposite_odds
    away_now_euro = home_now_euro.opposite_odds
    away_odds_summary.init_euro = away_init_euro
    away_odds_summary.now_euro = away_now_euro


def _gen_asia_odds(
    cid: str,
    asia_odds_list: list,
    home_odds_summary: OddsSummary,
    away_odds_summary: OddsSummary,
) -> None:
    odds = next((o for o in asia_odds_list if cid == o["cid"]), None)
    if not odds:
        return

    home_init_asia = AsiaOdds(
        goal_line=odds["initBet"],
        water_level=odds["initOddsUp"],
        return_rate=odds["initReturnRates"],
    )
    home_now_asia = AsiaOdds(
        goal_line=odds["nowBet"],
        water_level=odds["nowOddsUp"],
        return_rate=odds["nowReturnRates"],
    )
    home_odds_summary.init_asia = home_init_asia
    home_odds_summary.now_asia = home_now_asia

    goal_line = home_init_asia.goal_line * -1
    goal_line = 0.0 if goal_line == 0.0 else goal_line
    away_init_asia = AsiaOdds(
        goal_line=goal_line,
        water_level=odds["initOddsDown"],
        return_rate=odds["initReturnRates"],
    )

    goal_line = home_now_asia.goal_line * -1
    goal_line = 0.0 if goal_line == 0.0 else goal_line
    away_now_asia = AsiaOdds(
        goal_line=goal_line,
        water_level=odds["nowOddsDown"],
        return_rate=odds["nowReturnRates"],
    )

    away_odds_summary.init_asia = away_init_asia
    away_odds_summary.now_asia = away_now_asia
