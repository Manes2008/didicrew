import os
import sys
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Dam bao import config.py dung duong dan
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import config

def get_async_database_url() -> str:
    """Chuyen doi URL Database dong bo sang URL bat dong bo cho SQLAlchemy."""
    url = config.DATABASE_URL
    if url.startswith("postgresql+psycopg2://"):
        return url.replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("sqlite:///"):
        return url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
    return url

ASYNC_DATABASE_URL = get_async_database_url()

# Khoi tao Async Engine va SessionMaker
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,
    pool_recycle=300,
    pool_pre_ping=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI Dependency cung cap AsyncSession cho tung Request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
