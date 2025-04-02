from typing import List, Optional

import redis
from fastapi import APIRouter, File, UploadFile, HTTPException, Form

import utils.validators as validators
from controllers.video_controller import VideoController
from database.database_dto import OriginalVideoDTO, TrimmedVideoDTO
from models.file_type_model import FileData
from models.video_models import VideoUploadResponse, VideoProcessInfo, MediaType, VideoScreenType


def get_video_controller():
    controller = VideoController(None)
    yield controller


class VideoRouter:
    def __init__(self, redis_client: redis.Redis ):
        self.router = APIRouter(prefix="/videos", tags=["videos"])
        self.add_routes()
        self.video_controller = VideoController(None, None, redis_client)

    def add_routes(self):
        @self.router.post("/upload/", response_model=VideoUploadResponse)
        async def upload_video(
            file: Optional[UploadFile] = File(None),
            segment_time: Optional[int] = Form(None),
            skip_pairs: Optional[str] = Form(None),  # Accept as string
            screen_type: Optional[str] = Form(None),
            edit_type: Optional[str] = Form(None),
            start_time: Optional[int] = Form(None),
            end_time: Optional[int] = Form(None),
        ):
            if file is None:
                raise HTTPException(status_code=400, detail="File must be provided")

            # Parse skip_pairs string to list of tuples
            parsed_skip_pairs = validators.parse_tuple_string(skip_pairs)

            # Create VideoProcessInfo object
            video_process_info = VideoProcessInfo(
                media_type=MediaType.VIDEO,
                segment_time=segment_time,
                skip_pairs=parsed_skip_pairs,
                screen_type=VideoScreenType(screen_type),
                edit_type=edit_type,
                start_time=start_time,
                end_time=end_time
            )
            """Upload a video file for processing."""
            return await self.video_controller.upload(video_process_info, FileData(file=file))


        @self.router.get("/original_videos/", response_model=List[OriginalVideoDTO])
        async def get_all_original_videos(
        ):
            """Get all original videos."""
            return await self.video_controller.get_all_original_videos()

        @self.router.get("/trimmed_videos/{file_id}", response_model=List[TrimmedVideoDTO])
        async def get_trimmed_videos_by_original_file_id(
                file_id: str
        ):
            """Get all trimmed videos for a given original file ID."""
            return await self.video_controller.get_trimmed_videos_by_original_file_id(file_id)