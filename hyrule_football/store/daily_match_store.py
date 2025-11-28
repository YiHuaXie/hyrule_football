import json
from typing import List, Optional
import redis
from hyrule_football.schema import MatchInfo
from hyrule_football.config import settings


class DailyMatchStore:
    """每日赛事缓存

    存储结构：
    - 使用一个 Hash：match:info
      - field: match_id
      - value: MatchInfo 的 JSON 字符串
    """

    KEY = "match:info"

    def __init__(self) -> None:
        redis_url = settings.REDIS_DEFAULT_URL
        self.r = redis.Redis.from_url(redis_url, decode_responses=True)

    def save_matches(self, matches: List[MatchInfo]) -> None:
        if not matches:
            return

        self.r.delete(self.KEY)  # 清空所有比赛
        mapping = {m.match_id: json.dumps(m.model_dump(), ensure_ascii=False) for m in matches}
        self.r.hset(self.KEY, mapping=mapping)

    def get_match(self, match_id: str) -> Optional[MatchInfo]:
        """根据 match_id 读取一场比赛信息"""
        raw = self.r.hget(self.KEY, match_id)
        if raw is None:
            return None
        return MatchInfo(**json.loads(raw))

    def list_matches(self) -> List[MatchInfo]:
        """读取当前缓存中的所有 MatchInfo"""
        all_values = self.r.hvals(self.KEY)
        return [MatchInfo(**json.loads(v)) for v in all_values]


daily_match_store = DailyMatchStore()
