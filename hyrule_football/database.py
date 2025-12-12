from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from hyrule_football.config import settings
from typing import Dict

# 创建数据库引擎
engine = create_engine(
    settings.SQLITE_DB_URL,
    connect_args={"check_same_thread": False},  # SQLite 需要此参数
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()


def db_wrapper(func):
    """装饰器：自动管理数据库会话"""

    def wrapper(*args, **kwargs):
        db = SessionLocal()
        try:
            return func(db, *args, **kwargs)
        finally:
            db.close()

    return wrapper


def db_session():
    """上下文管理器：自动管理数据库会话"""

    from contextlib import contextmanager

    @contextmanager
    def _session():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    return _session()


def db_initialize():
    """初始化数据库 创建所有表"""
    Base.metadata.create_all(bind=engine)


def init_db():
    """初始化数据库 创建所有表"""
    Base.metadata.create_all(bind=engine)


def get_table_fields(table_name: str) -> Dict[str, str]:
    # 从 SQLAlchemy 模型中获取字段信息（包含注释）
    fields = {}

    # 遍历所有注册的模型
    for mapper in Base.registry.mappers:
        model_class = mapper.class_
        if hasattr(model_class, "__tablename__") and model_class.__tablename__ == table_name:
            for column in mapper.columns:
                field_name = column.name
                comment = column.comment if column.comment else ""
                fields[field_name] = comment

            return fields

    return {}
