import logging

from services.ffmpeg_service import FfmpegService
from services.video_service import VideoService

logger = logging.getLogger(__name__)

class UrlService:
    def __init__(self):
        self.video_service = VideoService(FfmpegService())

