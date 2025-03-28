from argparse import FileType
from typing import Optional

from fastapi import APIRouter, Form, Depends, HTTPException

from controllers.url_controller import UrlController
from controllers.video_controller import VideoController
from models.file_type_model import FileData
from models.video_models import VideoUploadResponse, VideoProcessInfo
from services.ffmpeg_service import FfmpegService
from services.video_service import VideoService
from utils import video_utils, validators


def get_url_controller():
    controller = UrlController()
    yield controller

class UrlRouter:

    def __init__(self):
        self.router = APIRouter(prefix="/url", tags=["url"])
        self.add_routes()

    def add_routes(self):
        @self.router.post("/upload/", response_model=VideoUploadResponse)
        async def upload_video(
                video_url: Optional[str] = Form(None),
                segment_time: Optional[int] = Form(None),
                skip_pairs: Optional[str] = Form(None),  # Accept as string
                screen_type: Optional[str] = Form(None),
                edit_type: Optional[str] = Form(None),
                start_time: Optional[int] = Form(None),
                end_time: Optional[int] = Form(None),
                controller: UrlController = Depends(get_url_controller)
        ):
            # Parse skip_pairs string to list of tuples
            parsed_skip_pairs = validators.parse_tuple_string(skip_pairs)

            # Create VideoProcessInfo object
            video_process_info = VideoProcessInfo(
                segment_time=segment_time,
                skip_pairs=parsed_skip_pairs,
                screen_type=screen_type,
                edit_type=edit_type,
                start_time=start_time,
                end_time=end_time
            )

            file_type : FileData = FileData(url=video_url)


            """Upload a video file for processing."""
            return await controller.upload(video_process_info, file_type)
