from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from hyrule_football.models.team import Team
from typing import List, Optional
from hyrule_football.utils import orm_apply_patch


class TeamRepo:
    """球队数据访问层"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, team_id: int) -> Optional[Team]:
        """根据 ID 获取球队"""
        result = await self.db.execute(select(Team).filter_by(id=team_id))
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Team]:
        """根据名称获取球队"""
        result = await self.db.execute(select(Team).filter_by(name=name))
        return result.scalar_one_or_none()

    async def get_by_oh_id(self, oh_id: str) -> Optional[Team]:
        """根据欧核 ID 获取球队"""
        result = await self.db.execute(select(Team).filter_by(oh_id=oh_id))
        return result.scalar_one_or_none()

    async def get_by_dqd_id(self, dqd_id: str) -> Optional[Team]:
        """根据懂球帝 ID 获取球队"""
        result = await self.db.execute(select(Team).filter_by(dqd_id=dqd_id))
        return result.scalar_one_or_none()

    async def create(self, name: str, oh_id: str, dqd_id: str = None) -> Team:
        """创建或更新球队"""
        existing = await self.get_by_oh_id(oh_id)
        if existing:
            return existing

        # 创建新记录
        team = Team(name=name, oh_id=oh_id, dqd_id=dqd_id)
        self.db.add(team)
        await self.db.flush()
        return team

    async def bind_dqd(self, team: Team, dqd_id: str) -> Team:
        """绑定懂球帝球队ID"""
        if team.dqd_id and team.dqd_id != dqd_id:
            return team

        team.dqd_id = dqd_id
        await self.db.flush()
        return team

    async def update(self, team: Team, **kwargs) -> Team:
        """更新球队信息"""
        orm_apply_patch(team, kwargs, protected_fields={"id", "name", "oh_id", "dqd_id"})
        await self.db.flush()
        return team

    async def delete(self, team_id: int) -> bool:
        """删除球队"""
        result = await self.db.execute(select(Team).filter_by(id=team_id))
        team = result.scalar_one_or_none()
        if not team:
            return False

        self.db.delete(team)
        await self.db.flush()
        return True

    # ========== 查询操作 ==========

    async def get_all(self) -> List[Team]:
        """获取所有球队"""
        result = await self.db.execute(select(Team))
        return list(result.scalars().all())

    async def get_teams_with_oh(self) -> List[Team]:
        """获取所有有欧核数据的球队"""
        result = await self.db.execute(select(Team).filter(Team.oh_id.isnot(None)))
        return list(result.scalars().all())

    async def get_teams_with_dqd(self) -> List[Team]:
        """获取所有有懂球帝数据的球队"""
        result = await self.db.execute(select(Team).filter(Team.dqd_id.isnot(None)))
        return list(result.scalars().all())

    async def get_teams_missing_dqd(self) -> List[Team]:
        """获取所有缺少懂球帝数据的球队"""
        result = await self.db.execute(select(Team).filter(Team.dqd_id.is_(None)))
        return list(result.scalars().all())
