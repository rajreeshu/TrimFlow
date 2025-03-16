import os
from pydantic_settings import BaseSettings

class Properties(BaseSettings):
    UPLOAD_DIR: str
    TRIMMED_DIR: str
    MAX_WORKERS: int
    CHUNK_SIZE: int
    SEGMENT_TIME: int
    DATABASE_URL: str
    
    class Config:
        env_file = os.path.join(os.path.dirname(__file__), '..', 'environment', f".env.{os.getenv('ENV', 'dev')}")

def ensure_directories_exist(properties: Properties):
    os.makedirs(properties.UPLOAD_DIR, exist_ok=True)
    os.makedirs(properties.TRIMMED_DIR, exist_ok=True)

properties = Properties()
ensure_directories_exist(properties)