from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm.attributes import flag_modified
from typing import List, Optional, Dict
from hyrule_football.models import StandardOdds


class StandardOddsRepo:
    """标准赔率数据访问层"""

    @staticmethod
    async def get_by_system(db: AsyncSession, system: str) -> Optional[StandardOdds]:
        """根据体系名称获取标准赔率数据"""
        result = await db.execute(select(StandardOdds).filter_by(system=system))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_or_update(db: AsyncSession, system: str, data: List[Dict]) -> StandardOdds:
        """创建或更新体系的赔率数据"""
        existing = await StandardOddsRepo.get_by_system(db, system)

        if existing:
            # 更新现有记录
            existing.data = data
            flag_modified(existing, "data")
            return existing
        else:
            # 创建新记录
            odds = StandardOdds(system=system, data=data)
            db.add(odds)
            await db.flush()
            return odds
