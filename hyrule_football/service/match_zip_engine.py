from typing import List, Optional, Dict, TypeAlias
from sqlalchemy.ext.asyncio import AsyncSession
from hyrule_football.schemas import MatchBase, DQDMatch
from hyrule_football.repositories.team_repo import TeamRepo
from hyrule_football.repositories.league_repo import LeagueRepo
from hyrule_football.models import League
from collections import defaultdict
from pydantic import ValidationError

DQDMatchesMap: TypeAlias = Dict[str, List[DQDMatch]]
OHMatches: TypeAlias = List[MatchBase]


class MatchZipEngine:

    def __init__(self, db: AsyncSession, leagues: List[League]):
        self.db = db
        self.oh_league_ids = [l.oh_id for l in leagues]
        self.dqd_league_ids = [l.dqd_id for l in leagues if l.dqd_id]

    def dqd_matches_map(self, matches: List[dict]) -> DQDMatchesMap:
        matches_map = defaultdict(list)
        valid_matches = []
        for m in matches:
            try:
                match = DQDMatch(**m)
            except Exception:
                continue
            valid_matches.append(match)

        for m in valid_matches:
            matches_map[m.competition_id].append(m)

        result = {k: v for k, v in matches_map.items() if k in self.dqd_league_ids}

        print(f"懂球帝有 {sum(len(v) for v in result.values())} 场比赛")
        return result

    def oh_matches(self, matches: List[dict]) -> OHMatches:
        valid_matches = []
        for m in matches:
            try:
                match = MatchBase(**m)
            except Exception:
                continue

            valid_matches.append(match)

        print(f"欧核有 {len(valid_matches)} 场比赛")

        return valid_matches

    async def matches_zip(
        self,
        matches: OHMatches,
        dqd_matches_map: DQDMatchesMap,
    ) -> List[MatchBase]:
        valid_matches = []
        for m in matches:
            db_league = await LeagueRepo.get_by_oh_id(self.db, m.oh_league_id)
            if not db_league:
                continue

            same_league_dqd_matches = dqd_matches_map.get(db_league.dqd_id, [])

            for dqd_m in same_league_dqd_matches:
                if await self._match_zip(m, dqd_m):
                    break

            valid_matches.append(m)

        print(f"合并后有 {len(valid_matches)} 场比赛")
        return valid_matches

    async def _match_zip(self, match: MatchBase, dqd_match: DQDMatch) -> bool:
        # 1. 判断比赛时间是否一致
        if match.match_time != dqd_match.start_play:
            return False

        # 2. 判断欧核和懂球帝的球队是否匹配
        home_team = await self._try_get_home_team(match, dqd_match)

        if home_team == "team_a":
            match.dqd_match_id = dqd_match.match_id
            match.dqd_home_team_id = dqd_match.team_A_id
            match.dqd_away_team_id = dqd_match.team_B_id
            return True

        if home_team == "team_b":
            match.dqd_match_id = dqd_match.match_id
            match.dqd_home_team_id = dqd_match.team_B_id
            match.dqd_away_team_id = dqd_match.team_A_id
            return True

        return False

    async def _try_get_home_team(self, match: MatchBase, dqd_match: DQDMatch) -> Optional[str]:
        if match.home == dqd_match.team_A_name or match.away == dqd_match.team_B_name:
            return "team_a"
        if match.home == dqd_match.team_B_name or match.away == dqd_match.team_A_name:
            return "team_b"

        team_repo = TeamRepo(self.db)
        home_team = await team_repo.get_by_oh_id(match.oh_home_team_id)
        if home_team and home_team.dqd_id:
            if home_team.dqd_id == dqd_match.team_A_id:
                return "team_a"
            if home_team.dqd_id == dqd_match.team_B_id:
                return "team_b"

        away_team = await team_repo.get_by_oh_id(match.oh_away_team_id)
        if away_team and away_team.dqd_id:
            if away_team.dqd_id == dqd_match.team_A_id:
                return "team_b"
            if away_team.dqd_id == dqd_match.team_B_id:
                return "team_a"

        return None
