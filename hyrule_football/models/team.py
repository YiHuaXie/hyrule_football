from sqlalchemy import Column, Integer, String, DateTime, func
from hyrule_football.database import Base


class Team(Base):
    """球队表 - 存储所有球队的基本信息"""

    __tablename__ = "team"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="球队ID")

    name = Column(String(100), nullable=False, unique=True, comment="球队名称")

    oh_id = Column(Integer, nullable=False, unique=True, comment="欧核球队ID")

    dqd_id = Column(String(64), nullable=True, unique=True, comment="懂球帝球队ID")

    created_at = Column(
        DateTime,
        server_default=func.now(),
        comment="创建时间",
    )

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        server_onupdate=func.now(),
        comment="更新时间",
    )

    # 表级约束
    __table_args__ = {"comment": "球队表"}
