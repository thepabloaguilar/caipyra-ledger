from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

from caipyra_ledger.configuration import settings

_db_engine = create_async_engine(
    settings.SQLALCHEMY_DB_URI,
    poolclass=NullPool,
    echo=settings.SQLALCHEMY_ECHO,
)

async_session = async_sessionmaker(
    bind=_db_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

@asynccontextmanager
async def get_session() -> AsyncIterator[AsyncSession]:
    async with async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
