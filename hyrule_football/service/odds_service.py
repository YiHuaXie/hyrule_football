from hyrule_football.schemas import (
    MatchBase,
    CompanyBase,
    MatchOddsDetail,
    OddsSummary,
    OddsPattern,
    CombineEuroOdds,
    CombineAsiaOdds,
)

from hyrule_football.utils import get_logger

from .standard_odds_service import StandardOddsEngine
import hyrule_football.service.oh_service as oh
from typing import List, Optional
import json

logger = get_logger(__name__)


async def get_odds_for_match(
    match_base: MatchBase,
    company_list: List[CompanyBase],
) -> Optional[MatchOddsDetail]:
    """获取某场比赛的赔率数据"""

    euro_odds_detail = oh.request_euro_odds_detail(match_base.oh_match_id)
    asia_odds_detail = oh.request_asia_odds_detail(match_base.oh_match_id)
    euro_odds_list = euro_odds_detail.get("oddsList", [])
    asia_odds_list = asia_odds_detail.get("oddsList", [])

    if not euro_odds_list and not asia_odds_list:
        return None

    odds_detail = MatchOddsDetail(match_base=match_base, company_list=company_list)

    for company in company_list:
        euro_odds = next((o for o in euro_odds_list if company.cid == o["cid"]), None)
        asia_odds = next((o for o in asia_odds_list if company.cid == o["cid"]), None)
        combine_euro_odds = CombineEuroOdds(**euro_odds) if euro_odds is not None else None
        combine_asia_odds = CombineAsiaOdds(**asia_odds) if asia_odds is not None else None

        home_odds_summary = OddsSummary(cid=company.cid, team_name=match_base.home)
        away_odds_summary = OddsSummary(cid=company.cid, team_name=match_base.away)

        if combine_euro_odds is not None:
            # 欧指：主队和客队的赔率是翻转关系
            home_init_euro = combine_euro_odds.to_init_odds
            home_now_euro = combine_euro_odds.to_now_odds
            away_init_euro = home_init_euro.flipped_odds
            away_now_euro = home_now_euro.flipped_odds

            home_odds_summary.init_euro = home_init_euro
            home_odds_summary.now_euro = home_now_euro
            away_odds_summary.init_euro = away_init_euro
            away_odds_summary.now_euro = away_now_euro

        if combine_asia_odds is not None:
            home_init_asia, away_init_asia = combine_asia_odds.to_init_odds
            home_now_asia, away_now_asia = combine_asia_odds.to_now_odds
            home_odds_summary.init_asia = home_init_asia
            home_odds_summary.now_asia = home_now_asia
            away_odds_summary.init_asia = away_init_asia
            away_odds_summary.now_asia = away_now_asia

        odds_pattern = OddsPattern(cid=company.cid)
        # 初始让球方的赔率汇总
        odds_summary = (
            home_odds_summary if home_odds_summary.init_asia.goal_line <= 0.0 else away_odds_summary
        )
        odds_pattern.init_team_name = odds_summary.team_name
        odds_pattern.init_pattern = await StandardOddsEngine.gen_pattern_str(
            odds_summary.init_euro, odds_summary.init_asia, match_base.league
        )
        # 即时让球方的赔率汇总
        odds_summary = (
            home_odds_summary if home_odds_summary.now_asia.goal_line <= 0.0 else away_odds_summary
        )
        odds_pattern.now_team_name = odds_summary.team_name
        odds_pattern.now_pattern = await StandardOddsEngine.gen_pattern_str(
            odds_summary.now_euro, odds_summary.now_asia, match_base.league
        )

        odds_detail.odds_pattern_list.append(odds_pattern)
        odds_detail.home_summary_list.append(home_odds_summary)
        odds_detail.away_summary_list.append(away_odds_summary)

    logger.info(
        f"✅ 已获取赔率数据：{json.dumps(odds_detail.model_dump(), indent=4, ensure_ascii=False)}"
    )
    return odds_detail
