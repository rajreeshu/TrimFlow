from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from config.config import config_properties


class Database:
    def __init__(self, database_url: str):
        self.engine = create_async_engine(database_url, echo=True)
        self.SessionLocal = sessionmaker(bind=self.engine, class_=AsyncSession, expire_on_commit=False)
        self.Base = declarative_base()

    async def get_db(self):
        async with self.SessionLocal() as session:
            yield session

# Initialize the database
database = Database(config_properties.DATABASE_URL)

# Access the Base class for models
Base = database.Base

# Dependency to get an async DB session
get_db = database.get_db

# Dependency to get the engine
engine=database.engine