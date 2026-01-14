from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from hyrule_football.models.league import League
from hyrule_football.utils import orm_apply_patch
from typing import List, Optional, Sequence


class LeagueRepo:
    """联赛数据访问层（单表设计）"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def commit(self):
        await self.db.commit()

    # ========== 基础 CRUD 操作 ==========

    async def get_by_id(self, league_id: int) -> Optional[League]:
        """根据 ID 获取联赛"""
        result = await self.db.execute(select(League).filter_by(id=league_id))
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[League]:
        """根据名称获取联赛"""
        result = await self.db.execute(select(League).filter_by(name=name))
        return result.scalar_one_or_none()

    async def get_by_oh_id(self, oh_id: int) -> Optional[League]:
        """根据欧核 ID 获取联赛"""
        result = await self.db.execute(select(League).filter_by(oh_id=oh_id))
        return result.scalar_one_or_none()

    async def create(self, name: str, oh_id: int, is_cup: int = 0) -> League:
        """创建联赛"""
        result = await self.db.execute(select(League).filter_by(name=name))
        existing = result.scalar_one_or_none()
        if existing:
            return existing

        # 创建新记录
        league = League(name=name, oh_id=oh_id, is_cup=is_cup)
        self.db.add(league)
        await self.db.flush()
        return league

    async def bind_dqd(self, league: League, dqd_id: str) -> League:
        """绑定懂球帝联赛ID"""
        if league.dqd_id and league.dqd_id != dqd_id:
            raise ValueError("dqd_id already bind")

        league.dqd_id = dqd_id
        await self.db.flush()
        return league

    async def update(self, league: League, **kwargs) -> League:
        """更新联赛信息"""
        orm_apply_patch(
            league,
            kwargs,
            protected_fields={"id", "name", "oh_id", "dqd_id"},
            allowed_fields={"oh_season", "oh_seasons", "dqd_season", "dqd_seasons", "is_cup"},
        )
        await self.db.flush()
        return league

    async def delete(self, league_id: int) -> bool:
        """删除联赛"""
        result = await self.db.execute(select(League).filter_by(id=league_id))
        league = result.scalar_one_or_none()
        if not league:
            return False

        self.db.delete(league)
        await self.db.flush()
        return True

    async def get_leagues_by_names(self, names: Sequence[str]) -> List[League]:
        """根据名称列表批量获取联赛"""
        if not names:
            return []

        stmt = select(League).where(League.name.in_(names))
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_leagues_with_both(self) -> List[League]:
        """获取所有同时有欧核和懂球帝数据的联赛"""
        stmt = select(League).where(League.oh_id.isnot(None), League.dqd_id.isnot(None))
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_leagues_with_missing_dqd(self) -> List[League]:
        """获取所有没有懂球帝数据的联赛"""
        result = await self.db.execute(select(League).filter(League.dqd_id.is_(None)))
        return list(result.scalars().all())

    async def get_all(self) -> List[League]:
        """获取所有联赛"""
        result = await self.db.execute(select(League))
        return list(result.scalars().all())
