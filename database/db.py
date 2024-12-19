from dotenv import load_dotenv
import os
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

load_dotenv()

Base = declarative_base()


async_engine = create_async_engine(
    url=f'{os.getenv("DB_URL")}'
)

async_session = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

