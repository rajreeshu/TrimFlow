import os
from pydantic_settings import BaseSettings

class Properties(BaseSettings):
    UPLOAD_DIR: str
    TRIMMED_DIR: str
    MAX_WORKERS: int
    CHUNK_SIZE: int
    DATABASE_URL: str
    PORT : str
    PROTOCOL : str
    BASE_URL : str
    COMPLETE_BASE_URL: str
    WIDTH_720P: int
    HEIGHT_720P: int
    TELEGRAM_BOT_TOKEN: str
    REDIS_HOST : str
    REDIS_PORT : int
    REDIS_DB : int
    REDIS_PASSWORD : str = ""  # Default to empty string if not provided
    REDIS_QUEUE_NAME : str

    
    class Config:
        env_file = os.path.join(os.path.dirname(__file__), '..', 'environment', f".env.{os.getenv('ENV', 'dev')}")

def ensure_directories_exist(properties: Properties):
    os.makedirs(properties.UPLOAD_DIR, exist_ok=True)
    os.makedirs(properties.TRIMMED_DIR, exist_ok=True)

config_properties = Properties()
ensure_directories_exist(config_properties)