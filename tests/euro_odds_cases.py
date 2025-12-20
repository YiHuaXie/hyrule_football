from hyrule_football.schemas import EuroOdds


def test_euro_odds():

    # 阿德莱德联 VS 墨尔本城
    euro = EuroOdds(w=2.82, d=3.59, l=2.27, return_rate=93.14)
    print(f"即时欧指:{euro}")
    print(f"欧指体系号:{euro.euro_system_no}")
    print(f"转化成 94:{euro.euro_odds_under_94}")


test_euro_odds()
