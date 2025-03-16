# database/repository/original_video_repository.py
from database.database_models import OriginalVideo
from database.repository.base_repository import BaseRepository

class OriginalVideoRepository(BaseRepository):
    def __init__(self):
        super().__init__(OriginalVideo)