from typing import List
from typing import Optional, Tuple, List
from hyrule_football.store import get_odds_store
from hyrule_football.models import StandardOdds, EuroOdds, AsiaOdds, EuroStandardOddsRange


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

    def euro_odds_pattern(self, euro: EuroOdds, asia: AsiaOdds) -> Optional[Tuple[str, str, str]]:
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

        return w_level, d_level, l_level

    # @staticmethod
    # def hyr_standard_odds_from_text(markdown_text: str) -> list[HYRStandardOdds]:
    #     html = markdown(markdown_text, extensions=["tables"])
    #     # 解析 HTML
    #     soup = BeautifulSoup(html, "lxml")
    #     rows = soup.find_all("tr")
    #     if len(rows) < 2:
    #         return []

    #     headers = [th.get_text(strip=True) for th in rows[0].find_all(["td", "th"])]
    #     # 解析数据行
    #     odds_list = []
    #     for row in rows[1:]:
    #         values = [td.get_text(strip=True) for td in row.find_all("td")]
    #         # 转成 model
    #         row_dict = dict(zip(headers, values))
    #         odds = HYRStandardOdds(**row_dict)
    #         odds_list.append(odds)

    #     return odds_list

    # @staticmethod
    # def hyr_standard_odds_from_file(markdown_path: str) -> list[HYRStandardOdds]:
    #     """从 markdown 中解析赔率数据列表生成 HYRStandardOdds 列表"""

    #     if not os.path.exists(markdown_path):
    #         raise FileNotFoundError(f"❌ 文件不存在: {markdown_path}")

    #     with open(markdown_path, "r", encoding="utf-8") as f:
    #         md_text = f.read().strip()
    #         return OddsEngine.hyr_standard_odds_from_text(md_text)

    # @staticmethod
    # def opposite_hry_standard_odds(odd_list: list[HYRStandardOdds]) -> list[HYRStandardOdds]:
    #     """将 HYRStandardOdds 列表中的欧指赔率转换为对立面"""
    #     new_list = []
    #     for odds in odd_list:
    #         new_odds = HYRStandardOdds(
    #             system=odds.system,
    #             interval=odds.interval,
    #             h=odds.a,
    #             d=odds.d,
    #             a=odds.h,
    #             return_rate=odds.return_rate,
    #             goal_line=odds.goal_line * -1,
    #             water_level=opposite_water_level(odds.water_level),
    #         )
    #         new_list.append(new_odds)

    #     return new_list

    # @staticmethod
    # def hyr_euro_odds_from_oh(odds: OHEuroOdds) -> HYREuroOdds:
    #     """从 OHEuroOdds 转成 HYREuroOdds"""
    #     return HYREuroOdds(
    #         cid=odds.cid,
    #         match_id=odds.matchId,
    #         h=float(odds.initOddsWin),
    #         d=float(odds.initOddsDraw),
    #         a=float(odds.initOddsLose),
    #     )

    # @staticmethod
    # def hyr_asis_odds_from_oh(odds: OHAsiaOdds) -> tuple[HYRAsiaOdds, HYRAsiaOdds]:
    #     """从 OHAsiaOdds 转成 HYRAsiaOdds 元组，先初始后即时"""
    #     init = HYRAsiaOdds(
    #         match_id=odds.matchId,
    #         cid=odds.cid,
    #         goal_line=odds.initGoalLine,
    #         water_level=odds.initWaterLevel,
    #     )
    #     print("初始亚盘")
    #     print(init.model_dump())

    #     now = HYRAsiaOdds(
    #         match_id=odds.matchId,
    #         cid=odds.cid,
    #         goal_line=odds.nowGoalLine,
    #         water_level=odds.nowWaterLevel,
    #     )
    #     print("即时亚盘")
    #     print(now.model_dump())

    #     return init, now

    # @staticmethod
    # def hyr_euro_odds_from_oh(odds: OHEuroOdds) -> tuple[HYREuroOdds, HYREuroOdds]:
    #     """从 OHEuroOdds 转成 HYREuroOdds 元组，先初始后即时"""

    #     init = HYREuroOdds(
    #         cid=odds.cid,
    #         match_id=odds.matchId,
    #         h=float(odds.initOddsWin),
    #         d=float(odds.initOddsDraw),
    #         a=float(odds.initOddsLose),
    #     )

    #     print("初始欧指")
    #     print(init.model_dump())

    #     now = HYREuroOdds(
    #         cid=odds.cid,
    #         match_id=odds.matchId,
    #         h=float(odds.nowOddsWin),
    #         d=float(odds.nowOddsDraw),
    #         a=float(odds.nowOddsLose),
    #     )
    #     print("即时欧指")
    #     print(now.model_dump())

    #     return init, now

    # @staticmethod
    # def hyr_standard_odds_from_oh_asia(
    #     list: list[HYRStandardOdds],
    #     asia: OHAsiaOdds,
    #     system: str,
    # ) -> tuple[list[HYRStandardOdds], list[HYRStandardOdds]]:
    #     """从 HYRStandardOdds 列表中过滤出符合 HYRAsiaOdds 的赔率数据"""
    #     init_hyr_asia, now_hyr_asia = OddsEngine.hyr_asis_odds_from_oh(asia)

    #     init = OddsEngine.hyr_standard_odds_from_hyr_asia(list, init_hyr_asia, system)
    #     now = OddsEngine.hyr_standard_odds_from_hyr_asia(list, now_hyr_asia, system)

    #     return init, now
