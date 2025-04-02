from typing import List

import redis
from fastapi import HTTPException
from telegram import Update
from telegram.ext import CallbackContext

from controllers.video_controller_interface import UploadControllerInterface
from database.database_dto import OriginalVideoDTO, TrimmedVideoDTO
from models.file_type_model import FileData
from models.video_models import VideoUploadResponse, VideoProcessInfo
from services.redis_service import RedisService
from services.video_service import VideoService


class VideoController(UploadControllerInterface):
    def __init__(self, update: Update, context: CallbackContext, redis_client: redis.Redis ):
        super().__init__(redis_client)
        self.video_service = VideoService(update, context, redis_client)
        self.redis_service = RedisService(redis_client)
    
    async def upload(self, video_process_info: VideoProcessInfo, file_data: FileData) -> VideoUploadResponse:
        if file_data.file is None:
            raise HTTPException(status_code=400, detail="File must be provided")
        file = file_data.file

        if video_process_info.skip_pairs is None:
            video_process_info.skip_pairs = []

        """Handle video upload request."""
        return await self.video_service.upload_and_send_to_redis(file, video_process_info)
        
        # return VideoUploadResponse(
        #     file_name=video_info.filename,
        #     file_id=video_info.file_id,
        #     status="Uploaded Successfully",
        #     message="Video processing started"
        # )

    async def get_all_original_videos(self) -> List[OriginalVideoDTO]:
        """Get all original videos."""
        return await self.video_service.get_all_original_videos()

    async def get_trimmed_videos_by_original_file_id(self, file_id: str) -> List[TrimmedVideoDTO]:
        """Get all trimmed videos for a given original file ID."""
        return await self.video_service.get_trimmed_videos_by_original_file_id(file_id)
