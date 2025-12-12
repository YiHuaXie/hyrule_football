from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    JSON,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from hyrule_football.database import Base


class Match(Base):

    __tablename__ = "match"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="赛事ID（自增）")

    oh_id = Column(String(64), nullable=True, index=True, comment="欧核联赛ID")

    dqd_id = Column(String(64), nullable=True, index=True, comment="懂球帝联赛ID")

    is_cup = Column(Integer, default=0, index=True, comment="是否为杯赛, 0: 否, 1: 是")

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
