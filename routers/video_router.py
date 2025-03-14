from fastapi import APIRouter, Depends, File, UploadFile
from controllers.video_controller import VideoController
from services.video_service import VideoService
from models.video_models import VideoUploadResponse, VideoInfo
from typing import List

router = APIRouter(prefix="/videos", tags=["videos"])

# Dependency
def get_video_controller():
    service = VideoService()
    controller = VideoController(service)
    yield controller
    service.shutdown()

@router.post("/upload/", response_model=VideoUploadResponse)
async def upload_video(
    file: UploadFile = File(...),
    controller: VideoController = Depends(get_video_controller)
):
    """Upload a video file for processing."""
    return await controller.upload_video(file)

@router.get("/status/{file_id}", response_model=VideoInfo)
def get_video_status(
    file_id: str,
    controller: VideoController = Depends(get_video_controller)
):
    """Get the status of a video processing job."""
    return controller.get_video_status(file_id)

@router.get("/", response_model=List[VideoInfo])
def get_all_videos(
    controller: VideoController = Depends(get_video_controller)
):
    """Get all video jobs."""
    return controller.get_all_videos()
