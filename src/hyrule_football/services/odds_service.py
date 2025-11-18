from hyrule_football.models import (
    MatchInfo,
    Company,
    BasedMatchOddsInfo,
    OddsSummary,
    Company,
    EuroOdds,
    AsiaOdds,
)
from typing import List
from hyrule_football.clients import HTTPClient
import os
from hyrule_football.utils import get_logger

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
        home_odds_summary = OddsSummary(
            company=company,
            team_name=match_info.home,
        )
        away_odds_summary = OddsSummary(
            company=company,
            team_name=match_info.away,
        )

        for odds in euro_odds_list:
            if company.cid != odds["cid"]:
                continue

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
            break

        for odds in asia_odds_list:
            if company.cid != odds["cid"]:
                continue

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
            break

        odds_info.home_summary_list.append(home_odds_summary)
        odds_info.away_summary_list.append(away_odds_summary)

    return odds_info
