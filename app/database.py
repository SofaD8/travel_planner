from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings


engine = create_async_engine(
    settings.DATABASE_URL,
    future=True,
    echo=False
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

class AsyncSessionContext:
    def __init__(self, session_factory):
        self.factory = session_factory

    async def __aenter__(self) -> AsyncSession:
        self.session = self.factory()
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

async def get_db():
    async with AsyncSessionContext(AsyncSessionLocal) as session:
        yield session
