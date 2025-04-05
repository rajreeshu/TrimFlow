from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config.config import config_properties

class Database:
    def __init__(self, database_url: str):
        # Remove async setup and keep only sync setup
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False
        )

        self.Base = declarative_base()

    def get_db(self):
        session = self.SessionLocal()
        try:
            return session
        except Exception:
            session.close()
            raise

# Initialize the database
database = Database(config_properties.DATABASE_URL)

# Access the Base class for models
Base = database.Base

# Dependencies
get_db = database.get_db

# Engine
engine = database.engine