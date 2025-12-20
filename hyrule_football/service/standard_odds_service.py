from hyrule_football.database import db_async_session
from hyrule_football.repositories.standard_odds_repo import StandardOddsRepo
from hyrule_football.schemas import StandardOddsBase, StandardOddsEuroRange, EuroOdds, AsiaOdds
from hyrule_football.utils import get_logger
from typing import List, Optional
import json
from pathlib import Path

logger = get_logger(__name__)


async def load_standard_odds_data():
    logger.info("🚀 同步标准赔率数据...")
    try:
        ODDS_DATA_DIR = Path(__file__).parent.parent / "data/odds"

        if not ODDS_DATA_DIR.exists():
            logger.warning(f"⚠️ 目录不存在: {ODDS_DATA_DIR}")
            return

        json_files = list(ODDS_DATA_DIR.glob("*.json"))

        if not json_files:
            logger.warning(f"⚠️ 目录中没有 JSON 文件")
            return

        systems_data = {}

        for json_file in json_files:
            system_name = json_file.stem
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                continue
            systems_data[system_name] = data

        # 导入到数据库
        async with db_async_session() as db:
            for system_name, data in systems_data.items():
                await StandardOddsRepo.create_or_update(db, system_name, data)

        logger.info(f"✅ 已同步 {len(systems_data)} 个体系的标准赔率数据")
    except Exception as e:
        logger.error(f"❌ 同步标准赔率数据失败: {e}")


class StandardOddsEngine:

    def __init__(self, system: str, standard_odds_list: List[StandardOddsBase]):
        self.system = system
        self.standard_odds_list = standard_odds_list

    @classmethod
    async def create(cls, system: str) -> "StandardOddsEngine":
        """异步工厂方法创建 StandardOddsEngine 实例"""
        async with db_async_session() as db:
            odds = await StandardOddsRepo.get_by_system(db, system)
            if odds and odds.data:
                standard_odds_list = [StandardOddsBase(**item) for item in odds.data]
            else:
                standard_odds_list = []

        return cls(system, standard_odds_list)

    @property
    def euro_odds_list(self) -> List[EuroOdds]:
        """转化为欧指赔率列表"""
        return [
            EuroOdds(w=odds.w, d=odds.d, l=odds.l, return_rate=odds.return_rate)
            for odds in self.standard_odds_list
        ]

    def filter_standard_odds_from_asia(self, asia: AsiaOdds) -> List[StandardOddsBase]:
        """过滤出符合 AsiaOdds 的赔率数据"""
        odds_list = []
        for odds in self.standard_odds_list:
            if odds.water_level != asia.water_level:
                continue
            if odds.goal_line != asia.goal_line:
                continue
            odds_list.append(odds)

        return odds_list

    @staticmethod
    def system_prefix_by_league(league_name: str) -> Optional[str]:
        system_prefix_map = {
            "英超": "英超",
            "西甲": "西甲",
            "法甲": "法甲",
            "意甲": "意甲",
            "德甲": "德甲",
        }

        return system_prefix_map.get(league_name, "通用")

    def _gen_pattern_str(self, euro: EuroOdds, asia: AsiaOdds) -> Optional[str]:
        """通过亚盘得出欧指胜平负的格局数据"""

        odds_list = self.filter_standard_odds_from_asia(asia)
        if not odds_list:
            return None

        odds_range = StandardOddsEuroRange.from_standard_odds_list(odds_list)

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
    async def gen_pattern_str(
        cls,
        euro_odds: Optional[EuroOdds],
        asia_odds: Optional[AsiaOdds],
        match_league: str,
    ) -> Optional[str]:
        """通过亚盘得出欧指胜平负的格局数据"""
        if not euro_odds or not asia_odds:
            return None

        system_prefix = StandardOddsEngine.system_prefix_by_league(match_league)

        async def _gen_pattern(euro, system_no):
            system_name = f"{system_prefix}{system_no}"
            engine = await StandardOddsEngine.create(system_name)
            return engine._gen_pattern_str(euro, asia_odds)

        # 1. 直接按当前体系尝试
        pattern = await _gen_pattern(euro_odds, euro_odds.euro_system_no)
        if pattern:
            return pattern

        # 2. 当前体系无结果 → 转换为94体系再尝试
        return await _gen_pattern(euro_odds.euro_odds_under_94, 94)
