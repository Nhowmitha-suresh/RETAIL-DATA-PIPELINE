from __future__ import annotations

import os
from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

DEFAULT_SQLITE_URL = 'sqlite+aiosqlite:///./data/retail.db'

_engine: AsyncEngine | None = None
_ENGINE_URL: str | None = None


def _make_engine(url: str) -> AsyncEngine:
    return create_async_engine(url, future=True, echo=False, pool_pre_ping=True)


def get_database_url() -> str:
    return os.environ.get('DATABASE_URL') or DEFAULT_SQLITE_URL


def init_engine(url: str | None = None) -> AsyncEngine:
    global _engine, _ENGINE_URL
    if url is None:
        url = get_database_url()
    if _engine is not None and _ENGINE_URL == url:
        return _engine
    _engine = _make_engine(url)
    _ENGINE_URL = url
    return _engine


def get_sessionmaker(engine: AsyncEngine) -> sessionmaker:
    return sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def _ensure_engine() -> AsyncEngine:
    global _engine, _ENGINE_URL
    engine = init_engine()
    try:
        async with engine.connect() as conn:
            await conn.execute(text('SELECT 1'))
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
