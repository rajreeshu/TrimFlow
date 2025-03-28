from fastapi import HTTPException
from telegram import Update
from telegram.ext import CallbackContext

from controllers.video_controller import VideoController
from controllers.video_controller_interface import UploadControllerInterface
from models.file_type_model import FileData
from models.video_models import VideoProcessInfo
from utils import video_utils


class UrlController(UploadControllerInterface):
    def __init__(self, update: Update, context: CallbackContext):
        super().__init__(update, context)
        self.video_controller = VideoController(update, context)

    async def upload(self, video_process_info: VideoProcessInfo, file_data: FileData):
        if not file_data:
            raise HTTPException(status_code=400, detail="File data is required")
        video_url = file_data.url
        file = None
        if video_url is not None:
            file = video_utils.download_online_video(video_url)
            if file is None:
                raise HTTPException(status_code=400, detail="No video found in the URL")

        """Upload a video file for processing."""
        return await self.video_controller.upload(video_process_info, FileData.generate(file))