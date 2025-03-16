from typing import List

from fastapi import APIRouter, Depends, File, UploadFile

from controllers.video_controller import VideoController
from models.video_models import VideoUploadResponse, VideoInfo
from services.video_service import VideoService


class VideoRouter:
    def __init__(self):
        self.router = APIRouter(prefix="/videos", tags=["videos"])
        self.add_routes()

    def get_video_controller(self):
        service = VideoService()
        controller = VideoController(service)
        yield controller
        service.shutdown()

    def add_routes(self):
        @self.router.post("/upload/", response_model=VideoUploadResponse)
        async def upload_video(
            file: UploadFile = File(...),
            controller: VideoController = Depends(self.get_video_controller)
        ):
            """Upload a video file for processing."""
            return await controller.upload_video(file)

        @self.router.get("/status/{file_id}", response_model=VideoInfo)
        def get_video_status(
            file_id: str,
            controller: VideoController = Depends(self.get_video_controller)
        ):
            """Get the status of a video processing job."""
            return controller.get_video_status(file_id)

        @self.router.get("/", response_model=List[VideoInfo])
        def get_all_videos(
            controller: VideoController = Depends(self.get_video_controller)
        ):
            """Get all video jobs."""
            return controller.get_all_videos()


        # @self.router.get("/original_videos", response_model=List[OriginalVideo])
        # async def get_all_original_videos(
        #     controller: VideoController = Depends(self.get_video_controller)
        # ):
        #     """Get all original video records."""
        #     return await controller.get_all_original_videos()