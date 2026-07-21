import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from loguru import logger
from sqlalchemy.orm import DeclarativeBase
load_dotenv()

USER_DB = os.getenv("USER_DB")
PASSWORD_DB = os.getenv("PASSWORD_DB")
HOST_DB = os.getenv("HOST_DB")
PORT_DB = os.getenv("PORT_DB")
DB_NAME = os.getenv("DB_NAME")

sqlalchemy_url = f'postgresql+asyncpg://{USER_DB}:{PASSWORD_DB}@{HOST_DB}:{PORT_DB}/{DB_NAME}'
engine = create_async_engine(sqlalchemy_url, pool_pre_ping=True, echo=False)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            logger.error(f'database error:', exc_info=True)
        raise
