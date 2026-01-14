from hyrule_football.database import db_async_session, safety_db_async_session
from hyrule_football.repositories.team_repo import TeamRepo
from hyrule_football.repositories.league_repo import LeagueRepo
from hyrule_football.models import League, Team
from hyrule_football.third_api import oh_api as oh
from hyrule_football.third_api import dqd_api as dqd
from hyrule_football.schemas import TeamSchemaDTO, TeamSchemaRank
from hyrule_football.service.base_sync_service import BaseSyncService
from hyrule_football.utils import get_logger, specific_season_name, Platform
from typing import List, Tuple, Set

logger = get_logger(__name__)


class TeamMapping:

    def __init__(self):
        self.main_teams: List[Tuple[TeamSchemaDTO, TeamSchemaRank]] = []

    async def mapping_teams_from_main(self, teams: List[TeamSchemaRank]):
        self.main_teams = []
        db_team_ids = set()
        async with safety_db_async_session() as db:
            try:
                repo = TeamRepo(db)
                for team in teams:
                    db_team = await repo.create(team.name, team.id)
                    if db_team.id not in db_team_ids:
                        team_dto = TeamSchemaDTO.model_validate(db_team)
                        self.main_teams.append((team_dto, team))
                        db_team_ids.add(db_team.id)
                await db.commit()
            except Exception as e:
                self.main_teams = []
                logger.error(f"mapping_teams_from_main failed: {e}")

    async def mapping_teams_from_dqd(self, dqd_teams: List[TeamSchemaRank]):
        async with safety_db_async_session() as db:
            try:
                repo = TeamRepo(db)
                for team_dto, team in self.main_teams:
                    db_team = await repo.get_by_id(team_dto.id)
                    matched_schema = next((t for t in dqd_teams if TeamSchemaRank.is_same_team(team, t)), None)
                    if matched_schema:
                        # print(f"{"*" * 30}")
                        # print(f"db team id:{db_team.id}, oh id:{db_team.oh_id}, dqd id:{db_team.dqd_id}")
                        # print(f"oh team:{team}")
                        # print(f"dqd team:{matched_schema}")
                        # print(f"{"*" * 30}")
                        await repo.bind_dqd(db_team, str(matched_schema.id))
                        team_dto.dqd_id = db_team.dqd_id
                await db.commit()
            except Exception as e:
                logger.error(f"mapping_teams_from_dqd failed: {e}")


class TeamSyncService(BaseSyncService):

    def __init__(self, platforms: Set[Platform]):
        super().__init__(platforms)
        if Platform.OH not in platforms:
            platforms.add(Platform.OH)
        self.mapping = TeamMapping()

    async def sync_teams_from_season(self, league_name: str, season_name: str) -> List[TeamSchemaDTO]:
        try:
            async with db_async_session() as db:
                league = await LeagueRepo(db).get_by_name(league_name)
                if not league:
                    raise ValueError(f"{league_name} not found")
                if league.is_cup == 1:
                    raise ValueError(f"{league.name} is a cup, no teams to sync")

            specific_season = specific_season_name(league.name, season_name)
            if not specific_season:
                raise ValueError(f"{league.name} {season_name} is not a valid season")

            await oh_sync_teams_from_season(specific_season, league, self.mapping)
            if Platform.DQD in self.platforms:
                await dqd_sync_teams_from_season(specific_season, league, self.mapping)

            return [t for t, _ in self.mapping.main_teams]
        except Exception as e:
            logger.error(f"sync_teams_from_season failed: {e}")
            return []


async def oh_sync_teams_from_season(specific_season: str, league: League, mapping: TeamMapping):
    try:
        seasons = league.oh_seasons or []
        if not seasons:
            raise ValueError(f"{league.name} has no oh seasons")
        season_id = next((s.get("id") for s in seasons if s.get("name") == specific_season), None)
        if not season_id:
            raise ValueError(f"{league.name} {specific_season} has no oh season id")

        teams = await oh.teams_from_season(league.oh_id, season_id)
        team_schemas = [TeamSchemaRank.from_oh_dict(t) for t in teams]
        await mapping.mapping_teams_from_main(team_schemas)
        if len(mapping.main_teams) == 0:
            raise ValueError(f"no main teams from oh")
    except Exception as e:
        logger.error(f"oh_sync_teams_from_season failed: {e}")
        raise e


async def dqd_sync_teams_from_season(specific_season: str, league: League, mapping: TeamMapping):
    try:
        seasons = league.dqd_seasons or []
        if not seasons:
            raise ValueError(f"{league.name} has no dqd seasons")
        season_id = next((s.get("id") for s in seasons if s.get("name") == specific_season), None)
        if not season_id:
            raise ValueError(f"{league.name} {specific_season} has no dqd season id")
        teams = await dqd.teams_from_season(season_id)
        team_schemas = [TeamSchemaRank.from_dqd_dict(t) for t in teams]
        await mapping.mapping_teams_from_dqd(team_schemas)
    except Exception as e:
        logger.error(f"dqd_sync_teams_from_season failed: {e}")
