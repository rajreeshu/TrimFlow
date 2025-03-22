import logging
from contextlib import asynccontextmanager

from sqlalchemy import select, and_

from database.database_config import database

logger = logging.getLogger(__name__)

class BaseRepository:
    def __init__(self, model):
        self.model = model

    @asynccontextmanager
    async def get_session(self):
        """Context manager for database sessions."""
        session = database.SessionLocal()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def save(self, instance):
        """Save an instance to the database."""
        async with self.get_session() as db:
            try:
                db.add(instance)
                await db.commit()
                await db.refresh(instance)
                return instance
            except Exception as e:
                logger.error(f"Error saving {self.model.__name__} data: {str(e)}")
                await db.rollback()
                raise

    async def get_all(self):
        """Retrieve all instances of the model."""
        async with self.get_session() as db:
            try:
                result = await db.execute(select(self.model).order_by(self.model.id.desc()))
                return result.scalars().all()
            except Exception as e:
                logger.error(f"Error retrieving all {self.model.__name__} data: {str(e)}")
                raise e

    async def get_by_id(self, instance_id):
        """Retrieve an instance by its ID."""
        async with self.get_session() as db:
            try:
                result = await db.execute(select(self.model).filter(self.model.id == instance_id))
                return result.scalars().first()
            except Exception as e:
                logger.error(f"Error retrieving {self.model.__name__} data: {str(e)}")
                raise e

    async def get_by_columns(self, column_value_map: dict):
        """Retrieve instances based on column-value pairs."""
        async with self.get_session() as db:
            try:
                conditions = [getattr(self.model, column) == value for column, value in column_value_map.items()]
                result = await db.execute(select(self.model).filter(and_(*conditions)))
                return result.scalars().all()
            except Exception as e:
                logger.error(
                    f"Error retrieving {self.model.__name__} data with conditions {column_value_map}: {str(e)}")
                raise e