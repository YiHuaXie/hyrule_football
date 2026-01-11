from hyrule_football.database import db_async_session
from hyrule_football.repositories.team_repo import TeamRepo
from hyrule_football.repositories.league_repo import LeagueRepo
from hyrule_football.models import League, Team
from hyrule_football.third_api import oh_api as oh
from hyrule_football.third_api import dqd_api as dqd
from hyrule_football.schemas import TeamRankSchema, Response
from hyrule_football.utils import get_logger, error_msg, specific_season_name
from typing import List, Tuple, TypeAlias, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio

logger = get_logger(__name__)


class TeamSyncInterface:

    @staticmethod
    async def sync_teams_from_season(db: AsyncSession, league: str, season: str) -> Response[List[Team]]:
        league_repo = LeagueRepo(db)
        db_league = await league_repo.get_by_name(league)
        if not league:
            return Response.failed(f"{league} 不存在")

        if league.is_cup == 1:
            return Response.failed(f"{league} 是杯赛，无法同步球队")

        standard_season = specific_season_name(league.name, season)
        if not standard_season:
            return Response.failed(f"{season} 不存在")

        teams = await TeamSyncService(db).sync_teams_from_season(db_league, standard_season)
        return Response.success(data=teams)


class TeamSyncService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.mapping = TeamMapping(db)

    async def sync_teams_from_season(self, league: League, season: str) -> List[Team]:
        if league.is_cup == 1:
            return []

        standard_season = specific_season_name(league.name, season)
        if not season:
            return []
        try:
            # 1. 同步欧核球队
            teams, season = await oh.teams_from_season(league.oh_id, season)
            team_schemas = [TeamRankSchema.from_oh_dict(t) for t in teams]
            tuples = await self.mapping.mapping_teams_from_main(team_schemas)

            season = specific_season_name(league.name, season)

            # 2. 同步懂球帝球队
            dqd_teams = []
            dqd_seasons = league.dqd_seasons or []
            dqd_season = next((s for s in dqd_seasons if s.get("name") == season), None)
            if dqd_season:
                dqd_teams = await dqd.teams_from_season(dqd_season.get("id"))
                dqd_team_schemas = [TeamRankSchema.from_dqd_dict(t) for t in dqd_teams]
                teams = await self.mapping.mapping_teams_from_dqd(dqd_team_schemas, tuples)

            await self.db.commit()
            return [t for t, _ in tuples]
        except Exception as e:
            logger.error(error_msg("sync_teams_from_season", e))
            return []


TeamMappingResult: TypeAlias = List[Tuple[Team, TeamRankSchema]]


class TeamMapping:

    def __init__(self, db: AsyncSession):
        self.repo = TeamRepo(db)

    async def mapping_teams_from_main(self, teams: List[TeamRankSchema]) -> TeamMappingResult:
        result = []
        db_team_ids = set()
        for team in teams:
            db_team = await self.repo.create(team.name, team.id)
            if db_team.id not in db_team_ids:
                result.append((db_team, team))
                db_team_ids.add(db_team.id)

        return result

    async def mapping_teams_from_dqd(self, dqd_teams: List[TeamRankSchema], tuples: TeamMappingResult):
        for db_team, team in tuples:
            matched = next((t for t in dqd_teams if TeamRankSchema.is_same_team(team, t)), None)
            if matched:
                await self.repo.bind_dqd(db_team, str(matched.id))


async def main():
    async with db_async_session() as db:
        from hyrule_football.repositories.league_repo import LeagueRepo

        league_repo = LeagueRepo(db)
        team_service = TeamSyncService(db)

        mzy = await league_repo.get_by_name("美职业")
        bj = await league_repo.get_by_name("比甲")
        ac = await league_repo.get_by_name("爱超")
        yc = await league_repo.get_by_name("英超")
        all_leagues = [(mzy, "2026"), (mzy, "2025"), (yc, "2025-2026"), (yc, "2024-2025")]  # ,
        for league, season in all_leagues:
            print(f"同步 {league.name} {season} 赛季下的球队...")
            teams = await team_service.sync_teams_from_season(league, season)
            print(f"✅ {league.name} {season} 赛季下的球队同步完成，共 {len(teams)} 支球队")


if __name__ == "__main__":
    asyncio.run(main())
