import redis
from typing import List, Dict, Any, Optional
import os


class RedisKeys:
    """Redis 中使用的 key"""

    # 洲 -> 联赛ID集合
    CONTINENT = "leagues:continent:{continentName}"

    # 联赛详情
    DETAIL = "leagues:data:{leagueId}"

    # 联赛名 -> 联赛ID
    NAME_TO_ID = "leagues:name_to_id"

    # 全部联赛ID
    ALL = "leagues:all"

    # 可选：国家 -> 联赛ID集合
    COUNTRY = "leagues:country:{countryId}"

    @staticmethod
    def continent_key(name: str) -> str:
        return RedisKeys.CONTINENT.format(continentName=name)

    @staticmethod
    def detail_key(league_id: str | int) -> str:
        return RedisKeys.DETAIL.format(leagueId=league_id)

    @staticmethod
    def country_key(country_id: str | int) -> str:
        return RedisKeys.COUNTRY.format(countryId=country_id)


class LeagueStore:

    def __init__(self):
        redis_url = os.getenv("REDIS_DEFAULT_URL")
        self.r = redis.Redis.from_url(redis_url, decode_responses=True)

    # ---------------------------------------------------------
    # 写入初始化数据
    # ---------------------------------------------------------
    def save_league_data(self, continent_list: List[Dict[str, Any]]):
        pipe = self.r.pipeline()

        for continent in continent_list:
            continent_name = continent["continentName"]
            league_list = continent["leagueList"]

            # 清空该洲旧数据
            pipe.delete(RedisKeys.continent_key(continent_name))

            for league in league_list:
                league_id = league["leagueId"]
                league_name = league["leagueName"]
                country_id = league.get("countryId")

                # 1. 保存联赛详情
                pipe.hset(RedisKeys.detail_key(league_id), mapping=league)

                # 2. 加入洲分类
                pipe.sadd(RedisKeys.continent_key(continent_name), league_id)

                # 3. 加入全部联赛集合
                pipe.sadd(RedisKeys.ALL, league_id)

                # 4. 名称 -> ID 映射
                pipe.hset(RedisKeys.NAME_TO_ID, league_name, league_id)

                # 5. （可选）按国家分类
                if country_id:
                    pipe.sadd(RedisKeys.country_key(country_id), league_id)

        pipe.execute()

    # ---------------------------------------------------------
    # 按洲查询
    # ---------------------------------------------------------
    def get_by_continent(self, continent_name: str) -> List[Dict[str, Any]]:
        ids = self.r.smembers(RedisKeys.continent_key(continent_name))
        return [self.get_by_id(i) for i in ids]

    # ---------------------------------------------------------
    # 按ID查询
    # ---------------------------------------------------------
    def get_by_id(self, league_id: str | int) -> Optional[Dict[str, Any]]:
        data = self.r.hgetall(RedisKeys.detail_key(league_id))
        return data if data else None

    # ---------------------------------------------------------
    # 按联赛名查询
    # ---------------------------------------------------------
    def get_by_name(self, league_name: str) -> Optional[Dict[str, Any]]:
        league_id = self.r.hget(RedisKeys.NAME_TO_ID, league_name)
        return self.get_by_id(league_id) if league_id else None

    # ---------------------------------------------------------
    # 获取全部联赛
    # ---------------------------------------------------------
    def get_all(self) -> List[Dict[str, Any]]:
        ids = self.r.smembers(RedisKeys.ALL)
        return [self.get_by_id(i) for i in ids]


_singleton_store: LeagueStore | None = None


def get_league_store() -> LeagueStore:
    global _singleton_store
    if _singleton_store is None:
        _singleton_store = LeagueStore()
    return _singleton_store
