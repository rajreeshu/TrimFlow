from fastapi import UploadFile, File

from database.database_dto import OriginalVideoDTO, TrimmedVideoDTO
from database.database_models import OriginalVideo
from services.video_service import VideoService
from models.video_models import VideoUploadResponse, VideoInfo, VideoProcessInfo
from typing import List

class VideoController:
    def __init__(self, video_service: VideoService):
        self.video_service = video_service
    
    async def upload_video(self, video_process_info: VideoProcessInfo, file: UploadFile = File(...)) -> VideoUploadResponse:
        """Handle video upload request."""
        video_info = await self.video_service.upload_and_process(file, video_process_info)
        
        return VideoUploadResponse(
            filename=video_info.filename,
            file_id=video_info.file_id,
            status="Uploaded Successfully",
            message="Video processing started"
        )
    
    def get_video_status(self, file_id: str) -> VideoInfo:
        """Get status of a video processing job."""
        return self.video_service.get_video_status(file_id)
    
    def get_all_videos(self) -> List[VideoInfo]:
        """Get all video jobs."""
        return self.video_service.get_all_videos()

    async def get_all_original_videos(self) -> List[OriginalVideoDTO]:
        """Get all original videos."""
        return await self.video_service.get_all_original_videos()

    async def get_trimmed_videos_by_original_file_id(self, file_id: str) -> List[TrimmedVideoDTO]:
        """Get all trimmed videos for a given original file ID."""
        return await self.video_service.get_trimmed_videos_by_original_file_id(file_id)
