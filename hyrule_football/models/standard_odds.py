from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    JSON,
)

from datetime import datetime, timezone
from hyrule_football.database import Base


class StandardOdds(Base):

    __tablename__ = "standard_odds"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    system = Column(String(50), nullable=False, unique=True, index=True, comment="体系名称")
    data = Column(JSON, nullable=False, comment="赔率数据")
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

    __table_args__ = ({"comment": "标准赔率表"},)

    def __repr__(self):
        data_count = len(self.data) if self.data else 0
        return f"<StandardOdds(id={self.id}, system={self.system}, count={data_count})>"
