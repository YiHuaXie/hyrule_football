import json
import os
from typing import List, Optional

import redis

from app.models import MatchInfo
from app.utils import get_logger

logger = get_logger(__name__)


class MatchStore:
    """MatchInfo 的 Redis 缓存，提供简单的 CRUD 接口

    存储结构：
    - 使用一个 Hash：match:info
      - field: match_id
      - value: MatchInfo 的 JSON 字符串
    """

    KEY = "match:info"

    def __init__(self):
        redis_url = os.getenv("REDIS_DEFAULT_URL")
        self.r = redis.Redis.from_url(redis_url, decode_responses=True)

    # -----------------------------
    # Create / Update
    # -----------------------------

    def save_match(self, match: MatchInfo) -> None:
        """创建或更新一条 MatchInfo（以 match_id 作为唯一键）"""
        data = match.model_dump()
        self.r.hset(self.KEY, match.match_id, json.dumps(data, ensure_ascii=False))

    def save_matches(self, matches: List[MatchInfo]) -> None:
        """批量创建或更新多条 MatchInfo"""
        if not matches:
            return

        mapping = {
            m.match_id: json.dumps(m.model_dump(), ensure_ascii=False) for m in matches
        }
        self.r.hset(self.KEY, mapping=mapping)

    # -----------------------------
    # Read
    # -----------------------------

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

    # -----------------------------
    # Delete
    # -----------------------------

    def delete_match(self, match_id: str) -> bool:
        """删除指定 match_id 的比赛，返回是否删除成功"""
        return self.r.hdel(self.KEY, match_id) > 0

    def clear_all(self) -> None:
        """清空所有 MatchInfo 缓存"""
        self.r.delete(self.KEY)
        logger.info("✅ 已清空所有 MatchInfo 缓存")
        # logger.info("--------------------------------------------------------")
        # logger.info(f"{self.r.hvals(self.KEY)}")


_singleton_store: MatchStore | None = None


def get_match_store() -> MatchStore:
    global _singleton_store
    if _singleton_store is None:
        _singleton_store = MatchStore()
    return _singleton_store
