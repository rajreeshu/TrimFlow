from abc import ABC, abstractmethod

import redis

from models.file_type_model import FileData
from models.video_models import VideoProcessInfo


class UploadControllerInterface(ABC):
    def __init__(self, redis_client: redis.Redis ):
        self.redis_client = redis_client

    @abstractmethod
    def upload(self, video_process_info: VideoProcessInfo, file_data: FileData):
        pass