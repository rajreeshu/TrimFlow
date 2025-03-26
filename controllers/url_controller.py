from fastapi import  HTTPException

from controllers.video_controller import VideoController
from models.video_models import VideoProcessInfo
from services.ffmpeg_service import FfmpegService
from services.video_service import VideoService
from utils import video_utils, validators
from telegram import Update

class UrlController:
    def __init__(self, update: Update):
        self.video_controller = VideoController(VideoService(FfmpegService(), update))

    async def upload_from_url(self, video_process_info: VideoProcessInfo, video_url: str, ):
        file = None
        if video_url is not None:
            file = video_utils.download_online_video(video_url)
            if file is None:
                raise HTTPException(status_code=400, detail="No video found in the URL")

        """Upload a video file for processing."""
        return await self.video_controller.upload_video(video_process_info, file)