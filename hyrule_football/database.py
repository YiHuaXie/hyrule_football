# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker, Session
# from hyrule_football.config import settings
# from typing import Dict

# # 创建数据库引擎
# engine = create_engine(
#     settings.SQLITE_DB_URL,
#     connect_args={"check_same_thread": False},  # SQLite 需要此参数
# )

# # 创建会话工厂
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # 创建基类
# Base = declarative_base()


# def db_wrapper(func):
#     """装饰器：自动管理数据库会话"""

#     def wrapper(*args, **kwargs):
#         db = SessionLocal()
#         try:
#             return func(db, *args, **kwargs)
#         finally:
#             db.close()

#     return wrapper


# def db_session():
#     """上下文管理器：自动管理数据库会话"""

#     from contextlib import contextmanager

#     @contextmanager
#     def _session():
#         db = SessionLocal()
#         try:
#             yield db
#         finally:
#             db.close()

#     return _session()


# def db_initialize():
#     """初始化数据库 创建所有表"""
#     Base.metadata.create_all(bind=engine)


# def init_db():
#     """初始化数据库 创建所有表"""
#     Base.metadata.create_all(bind=engine)


# def get_table_fields(table_name: str) -> Dict[str, str]:
#     # 从 SQLAlchemy 模型中获取字段信息（包含注释）
#     fields = {}

#     # 遍历所有注册的模型
#     for mapper in Base.registry.mappers:
#         model_class = mapper.class_
#         if hasattr(model_class, "__tablename__") and model_class.__tablename__ == table_name:
#             for column in mapper.columns:
#                 field_name = column.name
#                 comment = column.comment if column.comment else ""
#                 fields[field_name] = comment

#             return fields

#     return {}

import contextlib
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from hyrule_football.config import settings

Base = declarative_base()

async_engine = create_async_engine(
    settings.MYSQL_DB_URL,
    echo=False,  # 开发时显示 SQL，生产环境改为 False
    pool_pre_ping=True,  # 连接池健康检查
)

# 异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def create_database_if_need():
    """创建 MySQL 数据库（如果不存在）"""
    db_name = settings.MYSQL_DB_URL.split("/")[-1]
    base_url = settings.MYSQL_DB_URL.rsplit("/", 1)[0]

    tmp_engine = create_async_engine(base_url, isolation_level="AUTOCOMMIT")

    async with tmp_engine.connect() as conn:
        # 创建数据库
        await conn.execute(
            text(
                f"CREATE DATABASE IF NOT EXISTS {db_name} "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        )

        print(f"✅ 数据库 {db_name} 创建成功（或已存在）")

    await tmp_engine.dispose()


async def init_database_tables():
    """创建 MySQL 所有表（异步）"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("✅ MySQL 所有表创建成功")


async def init_database():
    """完整初始化 MySQL：创建数据库 + 创建表"""
    await create_database_if_need()
    await init_database_tables()


@contextlib.asynccontextmanager
async def db_async_session():
    """异步数据库会话上下文管理器"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
