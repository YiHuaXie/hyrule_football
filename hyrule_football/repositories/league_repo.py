from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from hyrule_football.models.league import League
from typing import List, Optional


class LeagueRepo:
    """联赛数据访问层（单表设计）"""

    # ========== 基础 CRUD 操作 ==========

    @staticmethod
    async def get_by_id(db: AsyncSession, league_id: int) -> Optional[League]:
        """根据 ID 获取联赛"""
        result = await db.execute(select(League).filter_by(id=league_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> Optional[League]:
        """根据名称获取联赛"""
        result = await db.execute(select(League).filter_by(name=name))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_oh_id(db: AsyncSession, oh_id: int) -> Optional[League]:
        """根据欧核 ID 获取联赛"""
        result = await db.execute(select(League).filter_by(oh_id=oh_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_or_update(
        db: AsyncSession,
        name: str,
        oh_id: int,
        dqd_id: Optional[int] = None,
        is_cup: int = 0,
    ) -> League:
        """创建或更新联赛"""
        result = await db.execute(select(League).filter_by(name=name))
        existing = result.scalar_one_or_none()

        if existing:
            # 更新已存在的记录
            if oh_id is not None:
                existing.oh_id = oh_id
            if dqd_id is not None:
                existing.dqd_id = dqd_id
            if is_cup is not None:
                existing.is_cup = is_cup
            await db.flush()
            return existing

        # 创建新记录
        league = League(name=name, oh_id=oh_id, dqd_id=dqd_id, is_cup=is_cup)
        db.add(league)
        await db.flush()
        return league

    @staticmethod
    async def update(db: AsyncSession, league_id: int, **kwargs) -> Optional[League]:
        """
        更新联赛信息

        Args:
            league_id: 联赛ID
            **kwargs: 要更新的字段（name, oh_id, dqd_id, is_cup）
        """
        result = await db.execute(select(League).filter_by(id=league_id))
        league = result.scalar_one_or_none()
        if not league:
            return None

        for key, value in kwargs.items():
            if hasattr(league, key):
                setattr(league, key, value)

        await db.flush()
        return league

    @staticmethod
    async def delete(db: AsyncSession, league_id: int) -> bool:
        """删除联赛"""
        result = await db.execute(select(League).filter_by(id=league_id))
        league = result.scalar_one_or_none()
        if not league:
            return False

        db.delete(league)
        await db.flush()
        return True

    # ========== 查询操作 ==========

    @staticmethod
    async def get_all_cups(db: AsyncSession) -> List[League]:
        """获取所有杯赛"""
        result = await db.execute(select(League).filter_by(is_cup=1))
        return list(result.scalars().all())

    @staticmethod
    async def get_leagues_with_both(db: AsyncSession) -> List[League]:
        """获取所有同时有欧核和懂球帝数据的联赛"""
        result = await db.execute(
            select(League).filter(League.oh_id.isnot(None), League.dqd_id.isnot(None))
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_leagues_with_missing_dqd(db: AsyncSession) -> List[League]:
        """获取所有没有懂球帝数据的联赛"""
        result = await db.execute(select(League).filter(League.dqd_id.is_(None)))
        return list(result.scalars().all())

    @staticmethod
    async def get_leagues_with_dqd(db: AsyncSession) -> List[League]:
        """获取所有有懂球帝数据的联赛"""
        result = await db.execute(select(League).filter(League.dqd_id.isnot(None)))
        return list(result.scalars().all())

    @staticmethod
    async def get_all(db: AsyncSession) -> List[League]:
        """获取所有联赛"""
        result = await db.execute(select(League))
        return list(result.scalars().all())
