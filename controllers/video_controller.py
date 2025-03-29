from typing import List, Optional

from telegram import Update

from controllers.video_controller_interface import UploadControllerInterface
from database.database_dto import OriginalVideoDTO, TrimmedVideoDTO
from models.file_type_model import FileData
from models.video_models import VideoUploadResponse, VideoInfo, VideoProcessInfo, VideoJobInfo
from services.ffmpeg_service import FfmpegService
from services.video_service import VideoService
from telegram.ext import CallbackContext


class VideoController(UploadControllerInterface):
    def __init__(self, update: Update, context: CallbackContext):
        super().__init__(update, context)
        self.video_service = VideoService(FfmpegService(), update, context)
    
    async def upload(self, video_process_info: VideoProcessInfo, file_data: FileData) -> VideoUploadResponse:
        file = file_data.file
        # Set default values if not provided
        video_process_info.segment_time = video_process_info.segment_time or 55  # Default segment time
        video_process_info.start_time = video_process_info.start_time or 0
        video_process_info.end_time = video_process_info.end_time or 0

        if video_process_info.skip_pairs is None:
            video_process_info.skip_pairs = []

        """Handle video upload request."""
        job_info = await self.video_service.upload_and_process(file, video_process_info)
        
        return VideoUploadResponse(
            filename=job_info.video_info.filename,
            file_id=job_info.file_id,
            job_id=job_info.job_id,
            status="Uploaded Successfully",
            message="Video processing added to queue"
        )
    
    def get_video_status(self, file_id: str) -> VideoJobInfo:
        """Get status of a video processing job."""
        return self.video_service.get_video_status(file_id)
    
    def get_all_videos(self) -> List[VideoJobInfo]:
        """Get all video jobs."""
        return self.video_service.get_all_videos()

    async def get_all_original_videos(self) -> List[OriginalVideoDTO]:
        """Get all original videos."""
        return await self.video_service.get_all_original_videos()

    async def get_trimmed_videos_by_original_file_id(self, file_id: str) -> List[TrimmedVideoDTO]:
        """Get all trimmed videos for a given original file ID."""
        return await self.video_service.get_trimmed_videos_by_original_file_id(file_id)
