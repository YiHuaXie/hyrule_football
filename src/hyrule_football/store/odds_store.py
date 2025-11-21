import redis
import json
from typing import List, Optional
from data import DATA_ODDS_DIR
from dotenv import load_dotenv as _load_dotenv
from hyrule_football.utils import get_logger
from hyrule_football.models import StandardOdds, EuroOdds, AsiaOdds

import os

_load_dotenv()

logger = get_logger(__name__)

_league_list = ["英超", "西甲", "法甲", "意甲", "德甲", "通用"]


class OddsStore:
    """
    赔率存储类 - 双索引方案

    存储结构：
    1. Hash: odds:{system}:euro - 欧赔索引 (h:d:a -> JSON)
       用途：按欧赔快速查询、更新、删除
       时间复杂度：O(1)

    2. Set: odds:{system}:asia:{goal_line}:{water_level} - 亚盘索引
       用途：按亚盘快速查询（主要查询场景）
       时间复杂度：O(m)，m 是结果数量
    """

    def __init__(self):
        redis_url = os.getenv("REDIS_DEFAULT_URL")
        self.r = redis.Redis.from_url(redis_url, decode_responses=True)

        if not self._has_any_odds:
            self._import_all_odds_list()

    # -----------------------------
    # 辅助方法
    # -----------------------------

    def _make_euro_key(self, system_name: str) -> str:
        """生成欧赔索引 key"""
        return f"odds:{system_name}:euro"

    def _make_asia_key(self, system_name: str, goal_line: float, water_level: str) -> str:
        """生成亚盘索引 key"""
        return f"odds:{system_name}:asia:{goal_line}:{water_level}"

    def _asia_key_pattern(self, system_name: str):
        """生成亚盘索引 key 的通配符"""
        return f"odds:{system_name}:asia:*"

    def _make_euro_field(self, odds: StandardOdds) -> str:
        """生成欧赔 Hash field (w:d:l)"""
        return f"{odds.w}:{odds.d}:{odds.l}"

    def _make_euro_field_from_euro(self, euro: EuroOdds) -> str:
        """从 EuroOdds 生成欧赔 Hash field"""
        return f"{euro.w}:{euro.d}:{euro.l}"

    def _odds_to_json(self, odds: StandardOdds) -> str:
        """将 StandardOdds 转换为 JSON 字符串"""
        return json.dumps(odds.model_dump(), ensure_ascii=False, sort_keys=True)

    def _json_to_odds(self, json_str: str) -> StandardOdds:
        """将 JSON 字符串转换为 StandardOdds"""
        return StandardOdds(**json.loads(json_str))

    @property
    def _has_any_odds(self) -> bool:
        # 有任何一个以 "odds:" 开头的 key，就说明有数据
        return next(self.r.scan_iter("odds:*"), None) is not None

    def _import_all_odds_list(self):
        DATA_ODDS_DIR.mkdir(parents=True, exist_ok=True)
        for league in _league_list:
            for system_no in range(92, 97):
                system_name = f"{league}{system_no}"
                path = DATA_ODDS_DIR / f"{system_name}.json"
                if not path.exists():
                    continue

                with path.open("r", encoding="utf-8") as f:
                    odds_list = [StandardOdds(**item) for item in json.load(f)]
                    self.save_system_odds(system_name, odds_list=odds_list)

    # -----------------------------
    # Create / Update
    # -----------------------------

    def save_system_odds(
        self,
        system_name: str,
        odds_list: List[StandardOdds],
        merge: bool = False,
    ):
        if not odds_list:
            return

        # 如果不合并，先删除旧数据
        if not merge:
            self.delete_system_odds(system_name)

        pipeline = self.r.pipeline()
        euro_key = self._make_euro_key(system_name)

        # 用于去重（同一批数据中可能有重复的欧赔）
        seen_euro = set()

        for odds in odds_list:
            odds_json = self._odds_to_json(odds)
            euro_field = self._make_euro_field(odds)

            # 去重：如果已经处理过相同的欧赔，跳过
            if euro_field in seen_euro:
                continue
            seen_euro.add(euro_field)

            # 1. 保存到欧赔索引（Hash）
            # hset 会自动覆盖相同 field 的旧值，实现去重
            pipeline.hset(euro_key, euro_field, odds_json)

            # 2. 保存到亚盘索引（Set）
            asia_key = self._make_asia_key(system_name, odds.goal_line, odds.water_level)
            pipeline.sadd(asia_key, odds_json)

        pipeline.execute()

    # -----------------------------
    # READ
    # -----------------------------

    def load_system_odds(self, system_name: str) -> List[StandardOdds]:
        euro_key = self._make_euro_key(system_name)
        all_json = self.r.hvals(euro_key)

        if not all_json:
            return []

        odds_list = [self._json_to_odds(j) for j in all_json]

        return sorted(odds_list, key=lambda x: (x.w, x.d, x.l))

    def get_system_count(self, system_name: str) -> int:
        """获取体系的数据总数"""
        euro_key = self._make_euro_key(system_name)
        return self.r.hlen(euro_key)

    # -----------------------------
    # DELETE
    # -----------------------------

    def delete_system_odds(self, system_name: str):
        """删除整个体系的所有赔率"""
        pipeline = self.r.pipeline()

        # 1. 删除欧赔索引
        euro_key = self._make_euro_key(system_name)
        pipeline.delete(euro_key)

        # 2. 删除所有亚盘索引
        # 使用 scan_iter 遍历所有匹配的 key
        asia_pattern = self._asia_key_pattern(system_name)
        for key in self.r.scan_iter(asia_pattern):
            pipeline.delete(key)

        pipeline.execute()

    def delete_odds_by_euro(self, system_name: str, euro: EuroOdds):
        """删除某个体系中指定欧赔的数据"""
        euro_key = self._make_euro_key(system_name)
        euro_field = self._make_euro_field_from_euro(euro)

        # 先获取要删除的数据（需要知道亚盘信息才能删除亚盘索引）
        odds_json = self.r.hget(euro_key, euro_field)
        if not odds_json:
            return  # 数据不存在，直接返回

        odds = self._json_to_odds(odds_json)

        pipeline = self.r.pipeline()

        # 1. 从欧赔索引删除
        pipeline.hdel(euro_key, euro_field)

        # 2. 从亚盘索引删除
        asia_key = self._make_asia_key(system_name, odds.goal_line, odds.water_level)
        pipeline.srem(asia_key, odds_json)

        pipeline.execute()

    # -----------------------------
    # UPDATE 单条或批量
    # -----------------------------

    def update_odds(self, system_name: str, new_odds: StandardOdds):
        """更新某个标准赔率数据，如果不存在则新增"""
        self.update_odds_list(system_name, [new_odds])

    def update_odds_list(self, system_name: str, new_odds_list: List[StandardOdds]):
        """更新某个体系的多条欧赔数据，如果不存在则新增"""
        if not new_odds_list:
            return

        euro_key = self._make_euro_key(system_name)
        pipeline = self.r.pipeline()

        for new_odds in new_odds_list:
            euro_field = self._make_euro_field(new_odds)
            new_odds_json = self._odds_to_json(new_odds)

            # 检查是否已存在旧数据
            old_odds_json = self.r.hget(euro_key, euro_field)

            if old_odds_json:
                # 存在旧数据，需要先删除旧的亚盘索引
                old_odds = self._json_to_odds(old_odds_json)

                # 只有当亚盘信息改变时，才需要删除旧的亚盘索引
                if (
                    old_odds.goal_line != new_odds.goal_line
                    or old_odds.water_level != new_odds.water_level
                ):
                    # 删除旧的亚盘索引
                    old_asia_key = self._make_asia_key(
                        system_name, old_odds.goal_line, old_odds.water_level
                    )
                    pipeline.srem(old_asia_key, old_odds_json)

            # 添加新数据
            # 1. 更新欧赔索引（hset 会自动覆盖）
            pipeline.hset(euro_key, euro_field, new_odds_json)

            # 2. 添加到亚盘索引
            new_asia_key = self._make_asia_key(
                system_name, new_odds.goal_line, new_odds.water_level
            )
            pipeline.sadd(new_asia_key, new_odds_json)

        pipeline.execute()

    # -----------------------------
    # QUERY 条件查询
    # -----------------------------

    def query_odds_for_euro(self, system_name: str, euro: EuroOdds) -> Optional[StandardOdds]:
        """查询某体系的标准赔率（根据欧赔 h, d, a 三个字段）"""
        euro_key = self._make_euro_key(system_name)
        euro_field = self._make_euro_field_from_euro(euro)

        odds_json = self.r.hget(euro_key, euro_field)
        if not odds_json:
            return None

        return self._json_to_odds(odds_json)

    def query_odds_for_asia(self, system_name: str, asia: AsiaOdds) -> List[StandardOdds]:
        """
        查询某体系的符合亚盘的所有标准赔率（根据亚盘）
        这是主要查询场景，性能优化重点！
        """
        asia_key = self._make_asia_key(system_name, asia.goal_line, asia.water_level)
        all_json = self.r.smembers(asia_key)

        if not all_json:
            return []

        odds_list = [self._json_to_odds(j) for j in all_json]

        # 按 h 值排序返回
        return sorted(odds_list, key=lambda x: x.h)


_singleton_store: OddsStore | None = None


def get_odds_store() -> OddsStore:
    global _singleton_store
    if _singleton_store is None:
        _singleton_store = OddsStore()
    return _singleton_store


def _delete_all_odds():
    store = get_odds_store()
    pipeline = store.r.pipeline()
    for key in store.r.scan_iter("odds:*"):
        pipeline.delete(key)
    pipeline.execute()


def _export_all_odds():
    DATA_ODDS_DIR.mkdir(parents=True, exist_ok=True)
    store = get_odds_store()
    for league in _league_list:
        for system_no in range(92, 97):
            system_name = f"{league}{system_no}"
            odds_list = store.load_system_odds(system_name)
            if not odds_list:
                continue

            output_path = DATA_ODDS_DIR / f"{system_name}.json"
            with output_path.open("w", encoding="utf-8") as f:
                json.dump(
                    [odds.model_dump() for odds in odds_list], f, ensure_ascii=False, indent=2
                )
            logger.info(f"体系：{system_name}，数据量：{len(odds_list)}")


# _export_all_odds()
# store = odds_store_shared()
