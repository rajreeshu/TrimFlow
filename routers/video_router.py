from typing import List, Optional

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Form

from controllers.video_controller import VideoController
from database.database_dto import OriginalVideoDTO, TrimmedVideoDTO
from database.database_models import OriginalVideo
from models.video_models import VideoUploadResponse, VideoInfo, VideoProcessInfo, VideoScreenType, VideoEditType, VideoJobInfo
from services.ffmpeg_service import FfmpegService
from services.video_service import VideoService
import utils.validators as validators

import utils.video_utils as video_utils


def get_video_controller():
    controller = VideoController(None)
    yield controller


class VideoRouter:
    def __init__(self):
        self.router = APIRouter(prefix="/videos", tags=["videos"])
        self.add_routes()

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
            controller: VideoController = Depends(get_video_controller)
        ):
            if file is None:
                raise HTTPException(status_code=400, detail="File must be provided")

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
            """Upload a video file for processing."""
            return await controller.upload(video_process_info, file)

        @self.router.get("/status/{file_id}", response_model=VideoJobInfo)
        def get_video_status(
            file_id: str,
            controller: VideoController = Depends(get_video_controller)
        ):
            """Get the status of a video processing job."""
            return controller.get_video_status(file_id)
            
        @self.router.get("/job/{job_id}")
        def get_job_status(
            job_id: str
        ):
            """Get the status of a job directly from the queue."""
            from services.queue_service import get_job_status
            return get_job_status(job_id)

        @self.router.get("/", response_model=List[VideoJobInfo])
        def get_all_videos(
            controller: VideoController = Depends(get_video_controller)
        ):
            """Get all video jobs."""
            return controller.get_all_videos()

        @self.router.get("/original_videos/", response_model=List[OriginalVideoDTO])
        async def get_all_original_videos(
                controller: VideoController = Depends(get_video_controller)
        ):
            """Get all original videos."""
            return await controller.get_all_original_videos()

        @self.router.get("/trimmed_videos/{file_id}", response_model=List[TrimmedVideoDTO])
        async def get_trimmed_videos_by_original_file_id(
                file_id: str,
                controller: VideoController = Depends(get_video_controller)
        ):
            """Get all trimmed videos for a given original file ID."""
            return await controller.get_trimmed_videos_by_original_file_id(file_id)