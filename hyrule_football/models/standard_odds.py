from sqlalchemy import Column, Integer, String, DateTime, JSON, func
from hyrule_football.database import Base


class StandardOdds(Base):

    __tablename__ = "standard_odds"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")

    system = Column(String(50), nullable=False, unique=True, index=True, comment="体系名称")

    data = Column(JSON, nullable=False, comment="赔率数据")

    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    updated_at = Column(DateTime, server_default=func.now(), server_onupdate=func.now(), comment="更新时间")

    __table_args__ = ({"comment": "标准赔率表"},)

    def __repr__(self):
        data_count = len(self.data) if self.data else 0
        return f"<StandardOdds(id={self.id}, system={self.system}, count={data_count})>"
