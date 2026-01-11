from hyrule_football.repositories.league_repo import LeagueRepo
from hyrule_football.third_api import oh_api as oh
from hyrule_football.third_api import dqd_api as dqd
from hyrule_football.utils import get_logger, error_msg, Response, season_sort_key, Platform
from sqlalchemy.ext.asyncio import AsyncSession
from hyrule_football.models import League
from hyrule_football.schemas import LeagueSchema, SeasonSchema
from typing import List, Tuple, TypeAlias, Optional
from abc import ABC, abstractmethod

logger = get_logger(__name__)

filter_leagues_for_testing = ["英超", "意甲", "德甲", "西甲", "法甲", "欧冠杯", "欧洲杯"]


class LeagueSyncService(ABC):

    def __init__(self, db: AsyncSession):
        self.repo = LeagueRepo(db)
        self.mapping = LeagueMapping(db)

    @abstractmethod
    async def sync_leagues(self) -> List[League]:
        pass

    @abstractmethod
    async def sync_seasons_by_league(self, league: League) -> bool:
        pass

    def merge_seasons(self, db_seasons: List[SeasonSchema], new_seasons: List[SeasonSchema]) -> List[dict]:
        merged = (db_seasons or []) + (new_seasons or [])
        unique = {season.name: season for season in merged if season.name}
        sorted_seasons = sorted(unique.values(), key=lambda x: season_sort_key(x.name), reverse=True)
        return [s.model_dump() for s in sorted_seasons]


class OHLeagueSyncService(LeagueSyncService):

    async def sync_leagues(self) -> List[League]:
        try:
            leagues = await oh.request_league_list()
            schemas = [LeagueSchema.from_oh_dict(l) for l in leagues]
            tuples = await self.mapping.create_leagues_from_main(schemas)
            return [l for l, _ in tuples]
        except Exception as e:
            logger.error(error_msg("oh.sync_leagues", e))
            return []

    async def sync_seasons_by_league(self, league: League) -> bool:
        try:
            response = await oh.request_league_detail(league.oh_id)
            detail = response.get("data", {})
            detail["cup"] = league.is_cup

            schema = LeagueSchema.from_oh_dict(detail)
            if not schema:
                return False

            await self.repo.update(
                league,
                oh_season=schema.season.model_dump(),
                oh_seasons=self.merge_seasons(
                    [SeasonSchema(league=league.name, **s) for s in league.oh_seasons],
                    schema.seasons,
                ),
            )
            await self.repo.commit()
            return True
        except Exception as e:
            logger.error(error_msg("oh.sync_league_seasons", e))
            return False


class DQDLeagueSyncService(LeagueSyncService):

    async def sync_leagues(self) -> List[League]:
        try:
            leagues = await dqd.request_league_list()
            schemas = [LeagueSchema.from_dqd_dict(l) for l in leagues]
            tuples = await self.mapping.mapping_leagues_from_dqd(schemas)
            return [l for l, _ in tuples]
        except Exception as e:
            logger.error(error_msg("dqd.sync_leagues", e))
            return []

    async def sync_seasons_by_league(self, league: League) -> bool:
        try:
            seasons = await dqd.request_league_seasons(league.dqd_id)
            if not seasons:
                return False

            seasons = self.merge_seasons(
                [SeasonSchema(league=league.name, **s) for s in league.dqd_seasons],
                [SeasonSchema(league=league.name, **s) for s in seasons],
            )

            await self.repo.update(
                league,
                dqd_season=seasons[0] if seasons else None,
                dqd_seasons=seasons,
            )
            await self.repo.commit()
            return True
        except Exception as e:
            logger.error(error_msg("dqd.sync_league_seasons", e))
            return False


LeagueMappingResult: TypeAlias = List[Tuple[League, LeagueSchema]]


class LeagueMapping:

    def __init__(self, db: AsyncSession):
        self.repo = LeagueRepo(db)

    async def create_leagues_from_main(self, leagues: List[LeagueSchema]) -> LeagueMappingResult:
        result = []
        for schema in leagues:
            try:
                # 保去空不保去重
                if not schema:
                    continue
                league = await self.repo.create(schema.name, schema.id)
                await self.repo.update(league, is_cup=schema.is_cup)
                result.append((league, schema))
            except Exception as e:
                logger.error(error_msg("create_leagues_from_main.repo.create", e))
                continue

        await self.repo.commit()
        return result

    async def mapping_leagues_from_dqd(self, leagues: List[LeagueSchema]) -> LeagueMappingResult:
        result = []
        for schema in leagues:
            try:
                if not schema:
                    continue
                league = await self.repo.get_by_name(schema.name)
                if league:
                    await self.repo.bind_dqd(league, schema.id)
                    result.append((league, schema))
            except Exception as e:
                logger.error(error_msg("mapping_leagues_from_dqd.repo.bind_dqd", e))
                continue

        await self.repo.commit()
        return result
