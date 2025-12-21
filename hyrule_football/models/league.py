from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    func,
)

from hyrule_football.database import Base


class League(Base):
    """联赛表 - 存储所有联赛的基本信息"""

    __tablename__ = "league"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="联赛ID（自增）")
    name = Column(String(100), nullable=False, unique=True, comment="联赛名称")
    oh_id = Column(Integer, nullable=False, unique=True, comment="欧核联赛ID")
    dqd_id = Column(String(64), nullable=True, unique=True, comment="懂球帝联赛ID")
    is_cup = Column(Integer, default=0, comment="是否为杯赛：0=否，1=是")

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
    __table_args__ = {"comment": "联赛表"}
