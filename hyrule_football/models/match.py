from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Index,
)
from datetime import datetime, timezone
from hyrule_football.database import Base


class Match(Base):
    """赛事表"""

    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")

    oh_match_id = Column(
        String(64),
        nullable=False,
        unique=True,
        index=True,
        comment="欧核比赛ID",
    )

    dqd_match_id = Column(
        String(64),
        nullable=True,
        unique=True,
        index=True,
        comment="懂球帝比赛ID",
    )

    season = Column(String(20), nullable=False, index=True, comment="赛季，例如：2024-2025")

    # ========== 联赛信息 ==========
    league_id = Column(
        Integer,
        ForeignKey("league.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="联赛ID（外键）",
    )
    league = Column(String(100), nullable=False, index=True, comment="联赛名称")
    league_round = Column(String(50), nullable=True, comment="轮次，例如：第1轮")

    # ========== 比赛信息 ==========
    match_time = Column(
        String(20),
        nullable=False,
        index=True,
        comment="比赛时间（格式：YYYY-MM-DD HH:MM）",
    )

    match_state = Column(
        Integer,
        nullable=False,
        default=0,
        index=True,
        comment="比赛状态：0=未开赛, 1=进行中, 2=已完赛, 4=腰斩",
    )

    match_state_show = Column(String(20), nullable=True, comment="比赛状态文字")

    # ========== 主队信息 ==========
    home_id = Column(
        Integer,
        ForeignKey("team.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="主队ID（外键）",
    )
    home = Column(String(100), nullable=False, index=True, comment="主队名称")
    home_rank = Column(String(20), nullable=True, comment="主队排名")

    # ========== 客队信息 ==========
    away_id = Column(
        Integer,
        ForeignKey("team.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="客队ID（外键）",
    )
    away = Column(String(100), nullable=False, index=True, comment="客队名称")
    away_rank = Column(String(20), nullable=True, comment="客队排名")

    # ========== 时间戳 ==========
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="创建时间（UTC）",
    )

    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="更新时间（UTC）",
    )

    # ========== 关系 ==========
    # league_rel = relationship("League", back_populates="matches")
    # home_team_rel = relationship("Team", foreign_keys=[home_id], back_populates="home_matches")
    # away_team_rel = relationship("Team", foreign_keys=[away_id], back_populates="away_matches")

    # ========== 表级约束 ==========
    __table_args__ = (
        # 复合索引：联赛 + 赛季 + 比赛时间（常用查询组合）
        Index("idx_league_season_time", "league_id", "season", "match_time"),
        # 复合索引：联赛 + 比赛状态（查询某联赛的未开赛/进行中比赛）
        Index("idx_league_state", "league_id", "match_state"),
        # 复合索引：主队 + 比赛时间（查询某队的比赛历史）
        Index("idx_home_time", "home_id", "match_time"),
        # 复合索引：客队 + 比赛时间（查询某队的比赛历史）
        Index("idx_away_time", "away_id", "match_time"),
        {"comment": "赛事表"},
    )
