from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone
from hyrule_football.database import Base


class Team(Base):
    """球队表 - 存储所有球队的基本信息"""

    __tablename__ = "team"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="球队ID（自增）")

    name = Column(String(100), nullable=False, unique=True, comment="球队名称（唯一）")

    oh_id = Column(String(64), nullable=True, unique=True, comment="欧核球队ID（唯一，可为空）")

    dqd_id = Column(String(64), nullable=True, unique=True, comment="懂球帝球队ID（唯一，可为空）")

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        comment="创建时间（UTC）",
    )

    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        comment="更新时间（UTC）",
    )

    # 表级约束
    __table_args__ = {"comment": "球队表"}
