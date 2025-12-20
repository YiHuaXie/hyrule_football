from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone
from hyrule_football.database import Base


class Company(Base):

    __tablename__ = "company"

    id = Column(Integer, primary_key=True, comment="博彩公司ID")

    name = Column(
        String(100),
        nullable=False,
        index=True,
        unique=True,
        comment="博彩公司名称",
    )

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
    __table_args__ = {"comment": "博彩公司表"}

    def __repr__(self):
        return f"<Company(id={self.id}, name={self.name})>"
