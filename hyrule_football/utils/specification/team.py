from typing import Optional


def dqd_team_id_from_dqd(team_id: any) -> Optional[str]:
    try:
        team_id = int(team_id)
        if team_id > 50000000:
            team_id = team_id - 50000000
        return str(team_id) if team_id > 0 else None
    except (ValueError, TypeError):
        return None


def dqd_team_id_from_db(team_id: str) -> Optional[str]:
    try:
        team_id = int(team_id)
        if 0 < team_id < 50000000:
            return str(team_id + 50000000)
        elif team_id > 50000000:
            return str(team_id)
        else:
            return None
    except (ValueError, TypeError):
        return None
