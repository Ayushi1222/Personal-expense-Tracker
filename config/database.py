import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.settings import settings
from models.base import Base

engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)

async def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        await asyncio.to_thread(session.close)


async def init_db():
    def _init():
        Base.metadata.create_all(bind=engine)

    await asyncio.to_thread(_init)