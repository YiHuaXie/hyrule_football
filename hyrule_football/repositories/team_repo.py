from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from hyrule_football.models.team import Team
from typing import List, Optional


class TeamRepo:
    """球队数据访问层"""

    # ========== 基础 CRUD 操作 ==========

    @staticmethod
    async def get_by_id(db: AsyncSession, team_id: int) -> Optional[Team]:
        """根据 ID 获取球队"""
        result = await db.execute(select(Team).filter_by(id=team_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> Optional[Team]:
        """根据名称获取球队"""
        result = await db.execute(select(Team).filter_by(name=name))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_oh_id(db: AsyncSession, oh_id: str) -> Optional[Team]:
        """根据欧核 ID 获取球队"""
        result = await db.execute(select(Team).filter_by(oh_id=oh_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_dqd_id(db: AsyncSession, dqd_id: str) -> Optional[Team]:
        """根据懂球帝 ID 获取球队"""
        result = await db.execute(select(Team).filter_by(dqd_id=dqd_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_or_update(
        db: AsyncSession,
        name: str,
        oh_id: str = None,
        dqd_id: str = None,
    ) -> Team:
        """创建或更新球队"""
        result = await db.execute(select(Team).filter_by(name=name))
        existing = result.scalar_one_or_none()

        if existing:
            # 更新已存在的记录
            if oh_id is not None:
                existing.oh_id = oh_id
            if dqd_id is not None:
                existing.dqd_id = dqd_id
            await db.flush()
            return existing

        # 创建新记录
        team = Team(name=name, oh_id=oh_id, dqd_id=dqd_id)
        db.add(team)
        await db.flush()
        return team

    @staticmethod
    async def update(db: AsyncSession, team_id: int, **kwargs) -> Optional[Team]:
        """
        更新球队信息

        Args:
            team_id: 球队ID
            **kwargs: 要更新的字段（name, oh_id, dqd_id）
        """
        result = await db.execute(select(Team).filter_by(id=team_id))
        team = result.scalar_one_or_none()
        if not team:
            return None

        for key, value in kwargs.items():
            if hasattr(team, key):
                setattr(team, key, value)

        await db.flush()
        return team

    @staticmethod
    async def delete(db: AsyncSession, team_id: int) -> bool:
        """删除球队"""
        result = await db.execute(select(Team).filter_by(id=team_id))
        team = result.scalar_one_or_none()
        if not team:
            return False

        db.delete(team)
        await db.flush()
        return True

    # ========== 查询操作 ==========

    @staticmethod
    async def get_all(db: AsyncSession) -> List[Team]:
        """获取所有球队"""
        result = await db.execute(select(Team))
        return list(result.scalars().all())

    @staticmethod
    async def get_teams_with_oh(db: AsyncSession) -> List[Team]:
        """获取所有有欧核数据的球队"""
        result = await db.execute(select(Team).filter(Team.oh_id.isnot(None)))
        return list(result.scalars().all())

    @staticmethod
    async def get_teams_with_dqd(db: AsyncSession) -> List[Team]:
        """获取所有有懂球帝数据的球队"""
        result = await db.execute(select(Team).filter(Team.dqd_id.isnot(None)))
        return list(result.scalars().all())

    @staticmethod
    async def get_teams_missing_oh(db: AsyncSession) -> List[Team]:
        """获取所有缺少欧核数据的球队"""
        result = await db.execute(select(Team).filter(Team.oh_id.is_(None)))
        return list(result.scalars().all())

    @staticmethod
    async def get_teams_missing_dqd(db: AsyncSession) -> List[Team]:
        """获取所有缺少懂球帝数据的球队"""
        result = await db.execute(select(Team).filter(Team.dqd_id.is_(None)))
        return list(result.scalars().all())
