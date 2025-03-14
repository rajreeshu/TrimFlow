# filepath: c:\Users\reesh\OneDrive\Desktop\FB_Automation\Video_Trim\TrimFlow\database.py
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from databases import Database
from config.config import settings

DATABASE_URL = settings.DATABASE_URL

database = Database(DATABASE_URL)
metadata = MetaData()

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()