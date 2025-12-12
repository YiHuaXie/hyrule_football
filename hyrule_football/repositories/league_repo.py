from sqlalchemy.orm import Session
from hyrule_football.models.league import League
from typing import List, Optional


class LeagueRepo:
    """联赛数据访问层（单表设计）"""

    # ========== 基础 CRUD 操作 ==========

    @staticmethod
    def get_by_id(db: Session, league_id: int) -> Optional[League]:
        """根据 ID 获取联赛"""
        return db.query(League).filter_by(id=league_id).first()

    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[League]:
        """根据名称获取联赛"""
        return db.query(League).filter_by(name=name).first()

    @staticmethod
    def get_by_oh_id(db: Session, oh_id: str) -> Optional[League]:
        """根据欧核ID获取联赛"""
        return db.query(League).filter_by(oh_id=oh_id).first()

    @staticmethod
    def get_by_dqd_id(db: Session, dqd_id: str) -> Optional[League]:
        """根据懂球帝ID获取联赛"""
        return db.query(League).filter_by(dqd_id=dqd_id).first()

    @staticmethod
    def create(
        db: Session,
        name: str,
        oh_id: str = None,
        dqd_id: str = None,
        is_cup: int = 0,
    ) -> League:
        """
        创建联赛（如果 name 已存在则返回现有记录）

        Args:
            name: 联赛标准名称
            oh_id: 欧核联赛ID
            dqd_id: 懂球帝联赛ID
            is_cup: 是否为杯赛（0: 否, 1: 是）
        """
        existing = db.query(League).filter_by(name=name).first()
        if existing:
            return existing

        league = League(name=name, oh_id=oh_id, dqd_id=dqd_id, is_cup=is_cup)
        db.add(league)
        db.flush()
        return league

    @staticmethod
    def update(db: Session, league_id: int, **kwargs) -> Optional[League]:
        """
        更新联赛信息

        Args:
            league_id: 联赛ID
            **kwargs: 要更新的字段（name, oh_id, dqd_id, is_cup）
        """
        league = db.query(League).filter_by(id=league_id).first()
        if not league:
            return None

        for key, value in kwargs.items():
            if hasattr(league, key):
                setattr(league, key, value)

        db.flush()
        return league

    @staticmethod
    def update_oh_id(db: Session, league_id: int, oh_id: str) -> Optional[League]:
        """更新欧核ID"""
        league = db.query(League).filter_by(id=league_id).first()
        if not league:
            return None

        league.oh_id = oh_id
        db.flush()
        return league

    @staticmethod
    def update_dqd_id(db: Session, league_id: int, dqd_id: str) -> Optional[League]:
        """更新懂球帝ID"""
        league = db.query(League).filter_by(id=league_id).first()
        if not league:
            return None

        league.dqd_id = dqd_id
        db.flush()
        return league

    @staticmethod
    def delete(db: Session, league_id: int) -> bool:
        """删除联赛"""
        league = db.query(League).filter_by(id=league_id).first()
        if not league:
            return False

        db.delete(league)
        db.flush()
        return True

    # ========== 查询操作 ==========

    @staticmethod
    def get_all_cups(db: Session) -> List[League]:
        """获取所有杯赛"""
        return db.query(League).filter_by(is_cup=1).all()

    @staticmethod
    def get_all_leagues(db: Session) -> List[League]:
        """获取所有联赛（非杯赛）"""
        return db.query(League).filter_by(is_cup=0).all()

    @staticmethod
    def get_leagues_with_oh(db: Session) -> List[League]:
        """获取所有有欧核数据的联赛"""
        return db.query(League).filter(League.oh_id.isnot(None)).all()

    @staticmethod
    def get_leagues_with_dqd(db: Session) -> List[League]:
        """获取所有有懂球帝数据的联赛"""
        return db.query(League).filter(League.dqd_id.isnot(None)).all()

    @staticmethod
    def get_leagues_with_both(db: Session) -> List[League]:
        """获取所有同时有欧核和懂球帝数据的联赛"""
        return db.query(League).filter(League.oh_id.isnot(None), League.dqd_id.isnot(None)).all()

    @staticmethod
    def get_all(db: Session) -> List[League]:
        """获取所有联赛"""
        return db.query(League).all()
