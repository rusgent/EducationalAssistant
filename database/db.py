from dotenv import load_dotenv
import os
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

load_dotenv()

DATABASE_URL = os.getenv("DB_URL_POSTGRES")

async_engine = create_async_engine(
    url=DATABASE_URL
)

async_session = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

