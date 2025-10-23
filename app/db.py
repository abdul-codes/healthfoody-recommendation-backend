from sqlalchemy import Column, String, JSON, DateTime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./nutrition_cache.db")


class Base(DeclarativeBase):
    pass


class NutritionCache(Base):
    __tablename__ = "nutrition_cache"
    request_hash = Column(String, primary_key=True, index=True)
    response = Column(JSON)
    last_updated = Column(DateTime, default=datetime.utcnow)


# Create async engine and session factory
engine = create_async_engine(DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    await engine.dispose()
