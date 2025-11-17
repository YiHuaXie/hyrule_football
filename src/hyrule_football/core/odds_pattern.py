from hyrule_football.models import EuroOdds, EuroStandardOddsRange


def generate_euro_odds_pattern(euro: EuroOdds, odds_range: EuroStandardOddsRange):
    """生成当前胜平负赔率的格局数据"""

    def _level(value: float, low: float, high: float) -> str:
        if value < low:
            return "低"
        elif value > high:
            return "高"
        return "中"

    w_loc = _level(euro.w, odds_range.low_w, odds_range.hight_w)
    d_loc = _level(euro.d, odds_range.low_d, odds_range.hight_d)
    l_loc = _level(euro.l, odds_range.low_l, odds_range.hight_l)

    return w_loc, d_loc, l_loc
