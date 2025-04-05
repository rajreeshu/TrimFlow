from abc import ABC, abstractmethod

import redis

from models.file_type_model import FileData
from models.video_models import VideoProcessInfo


class UploadControllerInterface(ABC):
    @abstractmethod
    def upload(self, video_process_info: VideoProcessInfo, file_data: FileData, telegram_chat_id: int):
        pass