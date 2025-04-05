import logging
from contextlib import contextmanager
from sqlalchemy import select, and_
from database.database_config import database

logger = logging.getLogger(__name__)

class BaseRepository:
    def __init__(self, model):
        self.model = model

    @contextmanager
    def get_session(self):
        """Context manager for database sessions."""
        session = database.get_db()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def save(self, instance):
        """Save an instance to the database."""
        with self.get_session() as session:
            try:
                session.add(instance)
                session.commit()
                video_id = instance.id
                session.refresh(instance)
                return instance, video_id
            except Exception as e:
                logger.error(f"Error saving {self.model.__name__} data: {str(e)}")
                raise

    def get_all(self):
        """Retrieve all instances of the model."""
        with self.get_session() as db:
            try:
                result = db.execute(select(self.model).order_by(self.model.id.desc()))
                return result.scalars().all()
            except Exception as e:
                logger.error(f"Error retrieving all {self.model.__name__} data: {str(e)}")
                raise e

    def get_by_id(self, instance_id):
        """Retrieve an instance by its ID."""
        with self.get_session() as db:
            try:
                result = db.execute(select(self.model).filter(self.model.id == instance_id))
                return result.scalars().first()
            except Exception as e:
                logger.error(f"Error retrieving {self.model.__name__} data: {str(e)}")
                raise e

    def get_by_columns(self, column_value_map: dict):
        """Retrieve instances based on column-value pairs."""
        with self.get_session() as db:
            try:
                conditions = [getattr(self.model, column) == value for column, value in column_value_map.items()]
                result = db.execute(select(self.model).filter(and_(*conditions)))
                return result.scalars().all()
            except Exception as e:
                logger.error(
                    f"Error retrieving {self.model.__name__} data with conditions {column_value_map}: {str(e)}")
                raise e