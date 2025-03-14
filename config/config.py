import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    UPLOAD_DIR: str = "media/uploaded_videos"
    TRIMMED_DIR: str = "media/trimmed_videos"
    MAX_WORKERS: int = 4
    CHUNK_SIZE: int = 10 * 1024 * 1024  # 10MB
    SEGMENT_TIME: int = 60  # 60 seconds per segment
    DATABASE_URL: str = "postgresql://user:password@localhost/dbname"
    
    class Config:
        env_file = ".env"

settings = Settings()


# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.TRIMMED_DIR, exist_ok=True)