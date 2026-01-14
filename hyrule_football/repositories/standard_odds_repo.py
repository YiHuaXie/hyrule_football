from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm.attributes import flag_modified
from typing import List, Optional, Dict
from hyrule_football.models import StandardOdds


class StandardOddsRepo:

    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    async def get_by_system(self, system: str) -> Optional[StandardOdds]:
        """根据体系名称获取标准赔率数据"""
        result = await self.db.execute(select(StandardOdds).filter_by(system=system))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_or_update(self, system: str, data: List[Dict]) -> StandardOdds:
        """创建或更新体系的赔率数据"""
        existing = await self.get_by_system(system)

        if existing:
            # 更新现有记录
            existing.data = data
            flag_modified(existing, "data")
            return existing
        else:
            # 创建新记录
            odds = StandardOdds(system=system, data=data)
            self.db.add(odds)
            await self.db.flush()
            return odds
