from hyrule_football.schema import (
    MatchInfo,
    Company,
    BasedMatchOddsInfo,
    OddsSummary,
    Company,
    EuroOdds,
    AsiaOdds,
    OddsPattern,
)

from hyrule_football.utils import get_logger
from .odds_engine import OddsEngine
from .api_service import request_euro_odds_detail, request_asia_odds_detail

from typing import List
import json

logger = get_logger(__name__)


def get_odds_for_match(match_info: MatchInfo, company_list: List[Company]) -> BasedMatchOddsInfo:
    """获取某场比赛的赔率数据"""

    euro_odds_detail = request_euro_odds_detail(match_info.match_id)
    asia_odds_detail = request_asia_odds_detail(match_info.match_id)
    euro_odds_list = euro_odds_detail.get("oddsList", [])
    asia_odds_list = asia_odds_detail.get("oddsList", [])

    if not euro_odds_list and not asia_odds_list:
        return BasedMatchOddsInfo(match_info=match_info)

    odds_info = BasedMatchOddsInfo(match_info=match_info, company_list=company_list)

    for company in company_list:
        euro_data = _gen_euro_odds(company, euro_odds_list)
        asia_data = _gen_asia_odds(company, asia_odds_list)

        home_odds_summary = OddsSummary(cid=company.cid, team_name=match_info.home)
        home_odds_summary.init_asia = asia_data.get("home_init_asia")
        home_odds_summary.now_asia = asia_data.get("home_now_asia")
        home_odds_summary.init_euro = euro_data.get("home_init_euro")
        home_odds_summary.now_euro = euro_data.get("home_now_euro")

        away_odds_summary = OddsSummary(cid=company.cid, team_name=match_info.away)
        away_odds_summary.init_asia = asia_data.get("away_init_asia")
        away_odds_summary.now_asia = asia_data.get("away_now_asia")
        away_odds_summary.init_euro = euro_data.get("away_init_euro")
        away_odds_summary.now_euro = euro_data.get("away_now_euro")

        odds_pattern = _gen_pattern(
            company.cid, match_info.league, home_odds_summary, away_odds_summary
        )
        odds_info.odds_pattern_list.append(odds_pattern)
        odds_info.home_summary_list.append(home_odds_summary)
        odds_info.away_summary_list.append(away_odds_summary)

    logger.info(
        f"✅ 已获取赔率数据：{json.dumps(odds_info.model_dump(), indent=4, ensure_ascii=False)}"
    )
    return odds_info


def _gen_pattern(
    cid: int,
    match_league: str,
    home_summary: OddsSummary,
    away_summary: OddsSummary,
) -> OddsPattern:
    """生成格局数据"""

    odds_pattern = OddsPattern(cid=cid)
    # 初始让球方的赔率汇总
    odds_summary = home_summary if home_summary.init_asia.goal_line <= 0.0 else away_summary
    odds_pattern.init_team_name = odds_summary.team_name
    odds_pattern.init_pattern = OddsEngine.gen_pattern_str(
        odds_summary.init_euro, odds_summary.init_asia, match_league
    )
    # 即时让球方的赔率汇总
    odds_summary = home_summary if home_summary.now_asia.goal_line <= 0.0 else away_summary
    odds_pattern.now_team_name = odds_summary.team_name
    odds_pattern.now_pattern = OddsEngine.gen_pattern_str(
        odds_summary.now_euro, odds_summary.now_asia, match_league
    )

    return odds_pattern


def _gen_euro_odds(company: Company, euro_odds_list: list) -> dict:
    odds = next((o for o in euro_odds_list if company.cid == o["cid"]), None)
    if not odds:
        logger.warning(f"❌ 未找到 {company.name} 的欧指数据")
        return {}

    logger.info(f"原始欧指数据: {json.dumps(odds, indent=4, ensure_ascii=False)}")

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

    away_init_euro = home_init_euro.opposite_odds
    away_now_euro = home_now_euro.opposite_odds

    return {
        "home_init_euro": home_init_euro,
        "home_now_euro": home_now_euro,
        "away_init_euro": away_init_euro,
        "away_now_euro": away_now_euro,
    }


def _gen_asia_odds(company: Company, asia_odds_list: list) -> dict:
    odds = next((o for o in asia_odds_list if company.cid == o["cid"]), None)
    if not odds:
        logger.warning(f"❌ 未找到公司 {company.name} 的亚盘数据")
        return {}

    logger.info(f"原始亚盘数据: {json.dumps(odds, indent=4, ensure_ascii=False)}")

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

    return {
        "home_init_asia": home_init_asia,
        "home_now_asia": home_now_asia,
        "away_init_asia": away_init_asia,
        "away_now_asia": away_now_asia,
    }
