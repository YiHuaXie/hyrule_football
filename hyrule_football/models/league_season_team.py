from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Index,
    UniqueConstraint,
    ForeignKey,
)

from datetime import datetime, timezone
from hyrule_football.database import Base


class LeagueSeasonTeam(Base):
    """联赛赛季球队关联表 - 记录某个赛季某个联赛包含哪些球队"""

    __tablename__ = "league_season_team"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID（自增）")

    league_id = Column(Integer, ForeignKey("league.id"), nullable=False, comment="联赛ID（外键）")

    season = Column(String(20), nullable=False, comment="赛季，格式：2024-2025 or 2025")

    team_id = Column(Integer, ForeignKey("team.id"), nullable=False, comment="球队ID（外键）")

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        comment="创建时间",
    )

    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        comment="更新时间",
    )

    # 表级约束
    __table_args__ = (
        Index("idx_league_season", "league_id", "season"),
        Index("idx_team_season", "team_id", "season"),
        UniqueConstraint("league_id", "season", "team_id", name="uq_league_season_team"),
        {"comment": "联赛赛季球队关联表"},
    )
