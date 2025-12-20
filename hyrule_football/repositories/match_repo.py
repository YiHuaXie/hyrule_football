from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from hyrule_football.models.match import Match
from typing import List, Optional


class MatchRepo:
    """赛事数据访问层"""

    # ========== 基础 CRUD 操作 ==========

    @staticmethod
    async def get_by_id(db: AsyncSession, match_id: int) -> Optional[Match]:
        """根据 ID 获取比赛"""
        result = await db.execute(select(Match).filter_by(id=match_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_oh_match_id(db: AsyncSession, oh_match_id: str) -> Optional[Match]:
        """根据欧核比赛 ID 获取比赛"""
        result = await db.execute(select(Match).filter_by(oh_match_id=oh_match_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_dqd_match_id(db: AsyncSession, dqd_match_id: str) -> Optional[Match]:
        """根据懂球帝比赛 ID 获取比赛"""
        result = await db.execute(select(Match).filter_by(dqd_match_id=dqd_match_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_or_update(db: AsyncSession, oh_match_id: str, **kwargs) -> Match:
        """
        创建或更新比赛

        Args:
            db: 数据库会话
            oh_match_id: 欧核比赛ID（唯一标识）
            **kwargs: 其他字段
                - season: str (必填)
                - league_id: int (必填)
                - league: str (必填)
                - match_time: str (必填)
                - match_state: int (必填)
                - home_id: int (必填)
                - home: str (必填)
                - away_id: int (必填)
                - away: str (必填)
                - dqd_match_id: str (可选)
                - league_round: str (可选)
                - match_state_show: str (可选)
                - home_rank: str (可选)
                - away_rank: str (可选)
        """
        result = await db.execute(select(Match).filter_by(oh_match_id=oh_match_id))
        existing = result.scalar_one_or_none()

        if existing:
            # 更新已存在的记录
            for key, value in kwargs.items():
                if hasattr(existing, key) and value is not None:
                    setattr(existing, key, value)
            await db.flush()
            return existing

        # 创建新记录
        match = Match(oh_match_id=oh_match_id, **kwargs)
        db.add(match)
        await db.flush()
        return match

    @staticmethod
    async def update(db: AsyncSession, match_id: int, **kwargs) -> Optional[Match]:
        """
        更新比赛信息

        Args:
            match_id: 比赛ID
            **kwargs: 要更新的字段
        """
        result = await db.execute(select(Match).filter_by(id=match_id))
        match = result.scalar_one_or_none()
        if not match:
            return None

        for key, value in kwargs.items():
            if hasattr(match, key):
                setattr(match, key, value)

        await db.flush()
        return match

    @staticmethod
    async def delete(db: AsyncSession, match_id: int) -> bool:
        """删除比赛"""
        result = await db.execute(select(Match).filter_by(id=match_id))
        match = result.scalar_one_or_none()
        if not match:
            return False

        db.delete(match)
        await db.flush()
        return True

    # ========== 查询操作 ==========

    @staticmethod
    async def get_by_league(db: AsyncSession, league_id: int, limit: int = 100) -> List[Match]:
        """获取某联赛的比赛列表"""
        result = await db.execute(
            select(Match)
            .filter_by(league_id=league_id)
            .order_by(Match.match_time.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_by_league_and_season(
        db: AsyncSession, league_id: int, season: str, limit: int = 1000
    ) -> List[Match]:
        """获取某联赛某赛季的比赛列表"""
        result = await db.execute(
            select(Match)
            .filter_by(league_id=league_id, season=season)
            .order_by(Match.match_time.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_by_team(db: AsyncSession, team_id: int, limit: int = 100) -> List[Match]:
        """获取某球队的比赛列表（主场或客场）"""
        result = await db.execute(
            select(Match)
            .filter(or_(Match.home_id == team_id, Match.away_id == team_id))
            .order_by(Match.match_time.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_by_state(db: AsyncSession, match_state: int, limit: int = 100) -> List[Match]:
        """获取某状态的比赛列表"""
        result = await db.execute(
            select(Match)
            .filter_by(match_state=match_state)
            .order_by(Match.match_time.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_by_date(db: AsyncSession, date: str, limit: int = 1000) -> List[Match]:
        """获取某日期的比赛列表（date 格式：YYYY-MM-DD）"""
        result = await db.execute(
            select(Match)
            .filter(Match.match_time.like(f"{date}%"))
            .order_by(Match.match_time.asc())
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_upcoming_matches(db: AsyncSession, limit: int = 100) -> List[Match]:
        """获取未开赛的比赛列表"""
        result = await db.execute(
            select(Match).filter_by(match_state=0).order_by(Match.match_time.asc()).limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_live_matches(db: AsyncSession) -> List[Match]:
        """获取进行中的比赛列表"""
        result = await db.execute(
            select(Match).filter_by(match_state=1).order_by(Match.match_time.asc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_finished_matches(db: AsyncSession, limit: int = 100) -> List[Match]:
        """获取已完赛的比赛列表"""
        result = await db.execute(
            select(Match).filter_by(match_state=2).order_by(Match.match_time.desc()).limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_all(db: AsyncSession, limit: int = 1000) -> List[Match]:
        """获取所有比赛"""
        result = await db.execute(select(Match).order_by(Match.match_time.desc()).limit(limit))
        return list(result.scalars().all())
