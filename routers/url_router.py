from typing import Optional

import redis
from fastapi import APIRouter, Form

from controllers.url_controller import UrlController
from models.file_type_model import FileData
from models.video_models import VideoUploadResponse, VideoProcessInfo, VideoScreenType, MediaType
from utils import validators


class UrlRouter:

    def __init__(self):
        self.router = APIRouter(prefix="/url", tags=["url"])
        self.add_routes()
        self.url_controller = UrlController()

    def add_routes(self):
        @self.router.post("/upload/", response_model=VideoUploadResponse)
        async def upload_video(
                url: Optional[str] = Form(None),
                segment_time: Optional[int] = Form(None),
                skip_pairs: Optional[str] = Form(None),  # Accept as string
                screen_type: Optional[str] = Form(None),
                edit_type: Optional[str] = Form(None),
                start_time: Optional[int] = Form(None),
                end_time: Optional[int] = Form(None),
                media_type: str = Form(None),

        ):
            # Parse skip_pairs string to list of tuples
            parsed_skip_pairs = validators.parse_tuple_string(skip_pairs)

            # Create VideoProcessInfo object
            video_process_info = VideoProcessInfo(
                media_type=MediaType(media_type),
                segment_time=segment_time,
                skip_pairs=parsed_skip_pairs,
                screen_type=VideoScreenType(screen_type),
                edit_type=edit_type,
                start_time=start_time,
                end_time=end_time
            )

            file_type: FileData = FileData(url=url)

            return self.url_controller.upload(video_process_info, file_type, None)

