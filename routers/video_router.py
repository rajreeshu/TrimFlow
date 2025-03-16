from typing import List

from fastapi import APIRouter, Depends, File, UploadFile

from controllers.video_controller import VideoController
from database.database_dto import OriginalVideoDTO, TrimmedVideoDTO
from database.database_models import OriginalVideo
from models.video_models import VideoUploadResponse, VideoInfo
from services.ffmpeg_service import FfmpegService
from services.video_service import VideoService


def get_video_controller():
    service = VideoService(FfmpegService())
    controller = VideoController(service)
    yield controller
    service.shutdown()


class VideoRouter:
    def __init__(self):
        self.router = APIRouter(prefix="/videos", tags=["videos"])
        self.add_routes()

    def add_routes(self):
        @self.router.post("/upload/", response_model=VideoUploadResponse)
        async def upload_video(
            file: UploadFile = File(...),
            controller: VideoController = Depends(get_video_controller)
        ):
            """Upload a video file for processing."""
            return await controller.upload_video(file)

        @self.router.get("/status/{file_id}", response_model=VideoInfo)
        def get_video_status(
            file_id: str,
            controller: VideoController = Depends(get_video_controller)
        ):
            """Get the status of a video processing job."""
            return controller.get_video_status(file_id)

        @self.router.get("/", response_model=List[VideoInfo])
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