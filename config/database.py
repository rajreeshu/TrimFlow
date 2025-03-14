from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config.config import settings

DATABASE_URL = settings.DATABASE_URL

# Create an async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create an async session factory
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Define the base class for models
Base = declarative_base()

# Dependency to get an async DB session
async def get_db():
    async with SessionLocal() as session:
        yield session