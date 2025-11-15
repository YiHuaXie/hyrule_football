from hyrule_football.models.hyrule_odds import HYRStandardOdds, HYREuroOdds, HYRAsiaOdds, HYREuroOddsRange

def generate_euro_odds_pattern(euro: HYREuroOdds, standard_range: HYREuroOddsRange):
    def _level(value: float, low: float, high: float) -> str:
        if value < low:
            return "低"
        elif value > high:
            return "高"
        return "中"
    
    h_loc = _level(euro.h, standard_range.low_h, standard_range.hight_h)
    d_loc = _level(euro.d, standard_range.low_d, standard_range.hight_d)
    a_loc = _level(euro.a, standard_range.low_a, standard_range.hight_a)
    
    return h_loc, d_loc, a_loc
