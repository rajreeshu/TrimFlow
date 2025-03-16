# database/repository/trimmed_video_repository.py
from database.database_models import TrimmedVideo
from database.repository.base_repository import BaseRepository

class TrimmedVideoRepository(BaseRepository):
    def __init__(self):
        super().__init__(TrimmedVideo)