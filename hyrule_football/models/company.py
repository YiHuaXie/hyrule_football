from sqlalchemy import Column, Integer, String, DateTime, func
from hyrule_football.database import Base


class Company(Base):

    __tablename__ = "company"

    id = Column(Integer, primary_key=True, comment="博彩公司ID")

    name = Column(String(100), nullable=False, index=True, unique=True, comment="博彩公司名称")

    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        server_onupdate=func.now(),
        comment="更新时间",
    )

    # 表级约束
    __table_args__ = {"comment": "博彩公司表"}

    def __repr__(self):
        return f"<Company(id={self.id}, name={self.name})>"
