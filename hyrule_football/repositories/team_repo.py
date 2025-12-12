from sqlalchemy.orm import Session
from hyrule_football.models.team import Team
from typing import List, Optional


class TeamRepo:
    """球队数据访问层"""

    # ========== 基础 CRUD 操作 ==========

    @staticmethod
    def get_by_id(db: Session, team_id: int) -> Optional[Team]:
        return db.query(Team).filter_by(id=team_id).first()

    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[Team]:
        return db.query(Team).filter_by(name=name).first()

    @staticmethod
    def get_by_oh_id(db: Session, oh_id: str) -> Optional[Team]:
        return db.query(Team).filter_by(oh_id=oh_id).first()

    @staticmethod
    def get_by_dqd_id(db: Session, dqd_id: str) -> Optional[Team]:
        return db.query(Team).filter_by(dqd_id=dqd_id).first()

    @staticmethod
    def get_or_create(
        db: Session,
        name: str,
        oh_id: str = None,
        dqd_id: str = None,
    ) -> Team:
        existing = db.query(Team).filter_by(name=name).first()
        if existing:
            return existing

        team = Team(name=name, oh_id=oh_id, dqd_id=dqd_id)
        db.add(team)
        db.flush()
        return team

    @staticmethod
    def update(db: Session, team: Team) -> Team:
        """
        更新球队信息

        注意：team 对象必须是从数据库查询出来的（已在 Session 中被追踪）

        Args:
            db: 数据库会话
            team: 从数据库查询出来的球队对象（已修改属性）

        Returns:
            更新后的球队对象

        Example:
            >>> team = TeamRepo.get_by_name(db, "曼联")
            >>> team.oh_id = "oh_new_123"
            >>> TeamRepo.update(db, team)
        """
        db.flush()
        return team

    @staticmethod
    def delete(db: Session, team_id: int) -> bool:
        team = db.query(Team).filter_by(id=team_id).first()
        if not team:
            return False

        db.delete(team)
        db.flush()
        return True

    # ========== 查询操作 ==========

    @staticmethod
    def get_all(db: Session) -> List[Team]:
        return db.query(Team).all()

    @staticmethod
    def get_teams_missing_oh(db: Session) -> List[Team]:
        return db.query(Team).filter(Team.oh_id.is_(None)).all()

    @staticmethod
    def get_teams_missing_dqd(db: Session) -> List[Team]:
        return db.query(Team).filter(Team.dqd_id.is_(None)).all()
