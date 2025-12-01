# from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
# from sqlalchemy.sql import func
# from hyrule_football.database import Base


# class League(Base):
#     """联赛模型"""

#     __tablename__ = "leagues"

#     leagueId = Column(Integer, primary_key=True, index=True, comment="联赛ID")
#     leagueName = Column(String(50), index=True, nullable=False, comment="联赛名称")

#     countryId = Column(Integer, index=True, nullable=False, comment="国家ID")
#     countryName = Column(String(50), index=True, nullable=False, comment="国家名称")

#     continentId = Column(Integer, index=True, nullable=False, comment="洲际ID")
#     continentName = Column(String(50), index=True, nullable=False, comment="洲际名称")

#     cup = Column(Integer, default=0, index=True, comment="是否为杯赛, 0: 否, 1: 是")

#     def __repr__(self):
#         return f"<League(leagueId={self.leagueId}, leagueName={self.leagueName})>"


# class SystemStandardOdds(Base):
#     """体系标准赔率模型"""

#     __tablename__ = "system_standard_odds"

#     id = Column(Integer, primary_key=True, index=True, comment="主键ID")
#     system = Column(String(50), index=True, nullable=False, comment="系统名称")
#     interval = Column(String(20), index=True, nullable=False, comment="区间")
#     w = Column(Float, nullable=False, comment="胜赔率")
#     d = Column(Float, nullable=False, comment="平赔率")
#     l = Column(Float, nullable=False, comment="负赔率")
#     return_rate = Column(Float, nullable=False, comment="返还率")
#     goal_line = Column(Float, nullable=False, comment="盘口")
#     water_level = Column(String(10), index=True, nullable=False, comment="水位等级")

#     def __repr__(self):
#         return f"<Odds(system={self.system}, interval={self.interval}, w={self.w}, d={self.d}, l={self.l})>"


# class Company(Base):
#     """博彩公司模型"""

#     __tablename__ = "company"

#     cid = Column(Integer, primary_key=True, index=True, comment="博彩公司ID")
#     name = Column(String(50), index=True, nullable=False, comment="博彩公司名称")

#     def __repr__(self):
#         return f"<Company(cid={self.cid}, name={self.name})>"

# # class Match(Base):
# #     """比赛模型"""
