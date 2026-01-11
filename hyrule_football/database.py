import contextlib
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import DeclarativeBase
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
