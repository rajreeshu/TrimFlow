from abc import ABC, abstractmethod
from typing import Optional

from telegram import Update
from telegram.ext import CallbackContext

from models.file_type_model import FileData
from models.video_models import VideoProcessInfo


class UploadControllerInterface(ABC):
    def __init__(self, update: Update, context: CallbackContext ):
        pass

    @abstractmethod
    async def upload(self, video_process_info: VideoProcessInfo, file_data: FileData):
        pass