from __future__ import annotations

import os
from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

DEFAULT_SQLITE_URL = 'sqlite+aiosqlite:///./data/retail.db'

# Public engine reference expected by other modules (e.g. api.main)
_engine: AsyncEngine | None = None
_ENGINE_URL: str | None = None
engine: AsyncEngine | None = None


def _make_engine(url: str) -> AsyncEngine:
    return create_async_engine(url, future=True, echo=False, pool_pre_ping=True)


def get_database_url() -> str:
    return os.environ.get('DATABASE_URL') or DEFAULT_SQLITE_URL


def init_engine(url: str | None = None) -> AsyncEngine:
    global _engine, _ENGINE_URL
    if url is None:
        url = get_database_url()
    if _engine is not None and _ENGINE_URL == url:
        # ensure public alias is set
        global engine
        engine = _engine
        return _engine
    _engine = _make_engine(url)
    _ENGINE_URL = url
    # expose public alias for convenience
    engine = _engine
    return _engine


def get_sessionmaker(engine: AsyncEngine) -> sessionmaker:
    return sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def _ensure_engine() -> AsyncEngine:
    global _engine, _ENGINE_URL
    engine = init_engine()
    try:
        async with engine.connect() as conn:
            await conn.execute(text('SELECT 1'))
        # keep public alias pointing to underlying engine
        global engine as _public_engine
        _public_engine = _engine
        return engine
    except Exception:
        if _ENGINE_URL != DEFAULT_SQLITE_URL:
            engine = init_engine(DEFAULT_SQLITE_URL)
            async with engine.connect() as conn:
                await conn.execute(text('SELECT 1'))
            return engine
        raise


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    engine = await _ensure_engine()
    async_session = get_sessionmaker(engine)
    async with async_session() as session:
        yield session


async def create_schema() -> None:
    engine = await _ensure_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def dispose_engine() -> None:
    """Dispose the async engine if created and clear references."""
    global _engine, engine
    if _engine is not None:
        try:
            await _engine.dispose()
        except Exception:
            pass
    _engine = None
    engine = None
