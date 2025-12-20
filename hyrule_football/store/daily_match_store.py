import json
from typing import List, Optional
import redis
from hyrule_football.schemas import MatchBase
from hyrule_football.config import settings


class DailyMatchStore:
    """每日赛事缓存

    存储结构：
    - 使用一个 Hash：match:base
      - field: match_id
      - value: MatchBase 的 JSON 字符串
    """

    KEY = "match:daily"

    def __init__(self) -> None:
        redis_url = settings.REDIS_DEFAULT_URL
        self.r = redis.Redis.from_url(redis_url, decode_responses=True)

    def save_matches(self, matches: List[MatchBase]) -> None:
        if not matches:
            return

        self.r.delete(self.KEY)  # 清空所有比赛
        mapping = {m.oh_match_id: json.dumps(m.model_dump(), ensure_ascii=False) for m in matches}
        self.r.hset(self.KEY, mapping=mapping)

    def get_match(self, oh_match_id: str) -> Optional[MatchBase]:
        """根据 match_id 读取一场比赛信息"""
        raw = self.r.hget(self.KEY, oh_match_id)
        if raw is None:
            return None
        return MatchBase(**json.loads(raw))

    def list_matches(self) -> List[MatchBase]:
        """读取当前缓存中的所有 MatchBase"""
        all_values = self.r.hvals(self.KEY)
        return [MatchBase(**json.loads(v)) for v in all_values]


daily_match_store = DailyMatchStore()
