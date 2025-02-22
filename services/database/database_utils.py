from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from contextlib import asynccontextmanager

class DatabaseUtils:
    _instance = None
    _session_pool = None
    _engine = None

    @classmethod
    def initialize(cls, db_config):
        if not cls._instance:
            cls._instance = cls()
            cls._engine = create_async_engine(
                db_config.construct_sqlalchemy_url(),
                query_cache_size=1200,
                pool_size=20,
                max_overflow=200,   
                future=True,
                echo=False,
            )
            cls._session_pool = async_sessionmaker(
                bind=cls._engine,
                expire_on_commit=False
            )
        return cls._instance

    @classmethod
    def get_session_pool(cls):
        if not cls._session_pool:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return cls._session_pool

    @classmethod
    @asynccontextmanager
    async def get_session(cls):
        if not cls._session_pool:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        async with cls._session_pool() as session:
            yield session