from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from .config import settings


class DataBaseHelper:
    def __init__(self):
        self.session_engine = create_async_engine(
            url=settings.dsn.encoded_string(),
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        self.session_factory = async_sessionmaker(
            bind=self.session_engine,
            expire_on_commit=False,
        )


db_helper = DataBaseHelper()
