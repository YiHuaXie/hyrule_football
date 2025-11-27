from typing import List
from typing import Optional, List
from app.store import get_odds_store
from app.models import StandardOdds, EuroOdds, AsiaOdds, EuroStandardOddsRange
from app.utils import get_league_name


class OddsEngine:

    def __init__(self, system: str):
        store = get_odds_store()
        self.standard_odds_list = store.load_system_odds(system)

    @property
    def euro_odds_list(self) -> List[EuroOdds]:
        """转化为欧指赔率列表"""
        return [
            EuroOdds(w=odds.w, d=odds.d, l=odds.l, return_rate=odds.return_rate)
            for odds in self.standard_odds_list
        ]

    def filter_standard_odds_from_asia(self, asia: AsiaOdds) -> List[StandardOdds]:
        """过滤出符合 AsiaOdds 的赔率数据"""
        odds_list = []
        for odds in self.standard_odds_list:
            if odds.water_level != asia.water_level:
                continue
            if odds.goal_line != asia.goal_line:
                continue
            odds_list.append(odds)

        return odds_list

    def _gen_pattern_str(self, euro: EuroOdds, asia: AsiaOdds) -> Optional[str]:
        """通过亚盘得出欧指胜平负的格局数据"""

        odds_list = self.filter_standard_odds_from_asia(asia)
        if not odds_list:
            return None

        odds_range = EuroStandardOddsRange.from_standard_odds_list(odds_list)

        def _level(value: float, low: float, high: float) -> str:
            if value < low:
                return "低"
            elif value > high:
                return "高"
            return "中"

        w_level = _level(euro.w, odds_range.low_w, odds_range.hight_w)
        d_level = _level(euro.d, odds_range.low_d, odds_range.hight_d)
        l_level = _level(euro.l, odds_range.low_l, odds_range.hight_l)

        return f"{w_level}-{d_level}-{l_level}"

    @classmethod
    def gen_pattern_str(
        cls,
        euro_odds: Optional[EuroOdds],
        asia_odds: Optional[AsiaOdds],
        match_league: str,
    ) -> Optional[str]:
        """通过亚盘得出欧指胜平负的格局数据"""
        if not euro_odds or not asia_odds:
            return None

        league_name = get_league_name(match_league)

        # 封装一次尝试逻辑
        def gen_pattern(euro, system_no):
            system_name = f"{league_name}{system_no}"
            engine = OddsEngine(system_name)
            return engine._gen_pattern_str(euro, asia_odds)

        # 1. 直接按当前体系尝试
        pattern = gen_pattern(euro_odds, euro_odds.euro_system_no)
        if pattern:
            return pattern

        # 2. 当前体系无结果 → 转换为94体系再尝试
        return gen_pattern(euro_odds.euro_odds_under_94, 94)
