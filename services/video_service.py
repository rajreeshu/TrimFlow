import logging
import os
from typing import List

import redis
from fastapi import HTTPException, UploadFile
from telegram import Update
from telegram.ext import CallbackContext

import utils.validators as validators
import utils.video_utils as video_utils
from config.config import config_properties
from database.database_dto import OriginalVideoDTO, TrimmedVideoDTO
from database.repository.original_video_repository import OriginalVideoRepository
from database.repository.trimmed_video_repository import TrimmedVideoRepository
from models.video_models import VideoProcessInfo, VideoUploadResponse
from services.redis_service import RedisService

logger = logging.getLogger(__name__)

class VideoService:
    def __init__(self, update: Update, context: CallbackContext):
        self.original_video_repo = OriginalVideoRepository()
        self.trimmed_video_repo = TrimmedVideoRepository()
        self.redis_service = RedisService()

    async def upload_and_send_to_redis(self, file : UploadFile, video_process_info : VideoProcessInfo) -> VideoUploadResponse:
        # Validate file
        validators.validate_video_file(file.filename)

        # Generate unique filename and ID
        unique_filename, file_id = validators.generate_unique_filename(file.filename)

        # Save video file
        file_path = os.path.join(config_properties.UPLOAD_DIR, unique_filename)
        await video_utils.save_file_in_chunks(file, file_path)

        video_process_info.url= validators.generate_full_path_from_location(file_path)

        self.redis_service.upload_to_redis(video_process_info)

        return VideoUploadResponse(
            file=unique_filename,
            file_id=file_id,
            status="Uploaded Successfully",
            message="Video processing started"
        )

    async def get_all_original_videos(self) -> List[OriginalVideoDTO]:
        """Retrieve all records from the OriginalVideo table."""
        try:
            original_videos = await self.original_video_repo.get_all()
            return [OriginalVideoDTO(**{**video.__dict__, "location": config_properties.COMPLETE_BASE_URL+"/"+video.location}) for video in original_videos]
        except Exception as e:
            logger.error(f"Error retrieving original videos: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to retrieve original videos: {str(e)}")

    async def get_trimmed_videos_by_original_file_id(self, file_id: str) -> List[TrimmedVideoDTO]:
        """Retrieve all trimmed videos for a given original file ID."""
        try:
            original_video_db_data = await self.original_video_repo.get_by_columns({"video_id": file_id})
            original_video_db_data = original_video_db_data[0]
            trimmed_videos = await self.trimmed_video_repo.get_by_columns({"original_video_id": original_video_db_data.id})

            return [TrimmedVideoDTO(**{**video.__dict__, "location":validators.generate_full_path_from_location(video.location) }) for video in trimmed_videos]
        except Exception as e:
            logger.error(f"Error retrieving trimmed videos for original file ID {file_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to retrieve trimmed videos: {str(e)}")

