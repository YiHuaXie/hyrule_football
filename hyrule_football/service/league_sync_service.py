from hyrule_football.repositories.league_repo import LeagueRepo
from hyrule_football.third_api import oh_api as oh
from hyrule_football.third_api import dqd_api as dqd
from hyrule_football.utils import get_logger, error_msg, season_sort_key, Platform
from hyrule_football.service.base_sync_service import BaseSyncService
from hyrule_football.database import safety_db_async_session
from hyrule_football.schemas import LeagueSchema, SeasonSchema
from typing import List, Set, Dict

logger = get_logger(__name__)

filter_leagues_for_testing = ["英超", "意甲", "德甲", "西甲", "法甲", "欧冠杯", "欧洲杯"]


class LeagueMapping:

    async def create_leagues_from_main(self, leagues: List[LeagueSchema]) -> List[LeagueSchema]:
        result = []
        async with safety_db_async_session() as db:
            repo = LeagueRepo(db)
            for schema in leagues:
                if not schema:
                    continue
                try:
                    await repo.create(schema.name, schema.id, schema.is_cup)
                    result.append(schema)
                except Exception as e:
                    logger.error(f"create_leagues_from_main, {e}")
                    continue

            await db.commit()
        return result

    async def mapping_leagues_from_dqd(self, leagues: List[LeagueSchema]) -> List[LeagueSchema]:
        result = []
        async with safety_db_async_session() as db:
            repo = LeagueRepo(db)
            for schema in leagues:
                if not schema:
                    continue
                try:
                    league = await repo.get_by_name(schema.name)
                    if league:
                        await repo.bind_dqd(league, schema.id)
                        result.append(schema)
                except Exception as e:
                    logger.error(f"mapping_leagues_from_dqd, {e}")
                    continue

            await db.commit()
        return result


class LeagueSyncService(BaseSyncService):

    def __init__(self, platforms: Set[Platform]):
        super().__init__(platforms)
        self.mapping = LeagueMapping()

    async def sync_leagues(self) -> Dict[Platform, List[LeagueSchema]]:
        result = {}
        if Platform.OH in self.platforms:
            leagues = await oh_sync_leagues(self.mapping)
            result[Platform.OH] = leagues
        if Platform.DQD in self.platforms:
            leagues = await dqd_sync_leagues(self.mapping)
            result[Platform.DQD] = leagues
        return result

    async def sync_seasons_by_league(self, league_id: int) -> Dict[Platform, bool]:
        result = {}
        if Platform.OH in self.platforms:
            result[Platform.OH] = await oh_sync_seasons_by_league(league_id)
        if Platform.DQD in self.platforms:
            result[Platform.DQD] = await dqd_sync_seasons_by_league(league_id)
        return result


async def oh_sync_leagues(mapping: LeagueMapping) -> List[LeagueSchema]:
    try:
        leagues = await oh.request_league_list()
        schemas = [LeagueSchema.from_oh_dict(l) for l in leagues]
        return await mapping.create_leagues_from_main(schemas)
    except Exception as e:
        logger.error(error_msg("oh_sync_leagues", e))
        return []


async def dqd_sync_leagues(mapping: LeagueMapping) -> List[LeagueSchema]:
    try:
        leagues = await dqd.request_league_list()
        # schemas = [schema for l in leagues if (schema := LeagueSchema.from_dqd_dict(l)) is not None]
        schemas = [LeagueSchema.from_dqd_dict(l) for l in leagues]
        return await mapping.mapping_leagues_from_dqd(schemas)
    except Exception as e:
        logger.error(error_msg("dqd_sync_leagues", e))
        return []


async def oh_sync_seasons_by_league(league_id: int) -> bool:
    async with safety_db_async_session() as db:
        try:
            repo = LeagueRepo(db)
            league = await repo.get_by_id(league_id)
            if not league:
                raise ValueError(f"league {league_id} not found")

            response = await oh.request_league_detail(league.oh_id)
            detail = response.get("data", {})
            detail["cup"] = league.is_cup

            schema = LeagueSchema.from_oh_dict(detail)
            if not schema:
                return False

            await repo.update(
                league,
                oh_season=schema.season.model_dump(),
                oh_seasons=_merge_seasons(
                    [SeasonSchema(league=league.name, **s) for s in league.oh_seasons],
                    schema.seasons,
                ),
            )
            return True
        except Exception as e:
            logger.exception(f"oh_sync_seasons_by_league, {e}")
            return False


async def dqd_sync_seasons_by_league(league_id: int) -> bool:
    async with safety_db_async_session() as db:
        try:
            repo = LeagueRepo(db)
            league = await repo.get_by_id(league_id)
            if not league:
                raise ValueError(f"league {league_id} not found")

            seasons = await dqd.request_league_seasons(league.dqd_id)
            if not seasons:
                return False

            await repo.update(
                league,
                dqd_season=seasons[0] if seasons else None,
                dqd_seasons=_merge_seasons(
                    [SeasonSchema(league=league.name, **s) for s in league.dqd_seasons],
                    [SeasonSchema(league=league.name, **s) for s in seasons],
                ),
            )
            return True
        except Exception as e:
            logger.error(f"dqd_sync_seasons_by_league, {e}")
            return False


def _merge_seasons(db_seasons: List[SeasonSchema], new_seasons: List[SeasonSchema]) -> List[dict]:
    merged = (db_seasons or []) + (new_seasons or [])
    unique = {season.name: season for season in merged if season.name}
    sorted_seasons = sorted(unique.values(), key=lambda x: season_sort_key(x.name), reverse=True)
    return [s.model_dump() for s in sorted_seasons]
