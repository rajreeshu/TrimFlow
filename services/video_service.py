from concurrent.futures import ThreadPoolExecutor
import os
from fastapi import UploadFile, HTTPException
import logging
import asyncio
from datetime import timedelta
from typing import Dict, List

from database.database_dto import OriginalVideoDTO, TrimmedVideoDTO
from database.repository.original_video_repository import OriginalVideoRepository
from database.repository.trimmed_video_repository import TrimmedVideoRepository
from models.video_models import VideoInfo, ProcessingStatus
import utils.file_utils as file_utils
import utils.validators as validators
import config.config as config
from database.database_models import OriginalVideo, TrimmedVideo
import services.subtitle_service as subtitle_service
from services.ffmpeg_service import FfmpegService

logger = logging.getLogger(__name__)

class VideoService:
    def __init__(self, ffmpeg_service: FfmpegService):
        self.executor = ThreadPoolExecutor(max_workers=config.config_properties.MAX_WORKERS)
        self.video_jobs: Dict[str, VideoInfo] = {}
        self.ffmpeg_service = ffmpeg_service
        self.original_video_repo = OriginalVideoRepository()
        self.trimmed_video_repo = TrimmedVideoRepository()

    async def upload_and_process(self, file: UploadFile) -> VideoInfo:
        """Upload a video file and submit for processing."""
        try:
            # Validate file
            validators.validate_video_file(file.filename)
            
            # Generate unique filename and ID
            unique_filename, file_id = validators.generate_unique_filename(file.filename)

            # Save video file
            file_path = os.path.join(config.config_properties.UPLOAD_DIR, unique_filename)
            await file_utils.save_file_in_chunks(file, file_path)

            # Save to database
            original_video = OriginalVideo(
                video_id=file_id,
                name=unique_filename,
                location=file_path,
                size=os.path.getsize(file_path),
                video_metadata={},  # Add any metadata if available
                created_user="system",  # Replace with actual user if available
                description="Uploaded video",
                category="Uncategorized",
                remark="",
                addon={}
            )

            await self.original_video_repo.save(original_video)

            movie_start_time = subtitle_service.find_movie_start_time(file_path)

            # Remove metadata from the video file
            cleaned_file_path = self.ffmpeg_service.remove_metadata(file_path)

            # Create video info object
            video_info = VideoInfo(
                file_id=file_id,
                filename=unique_filename,
                original_path=cleaned_file_path,
                status=ProcessingStatus.PENDING
            )

            # Submit for processing
            self.video_jobs[file_id] = video_info
            asyncio.create_task(self._process_video(file_id))
            
            return video_info

        except Exception as e:
            logger.error(f"Error processing upload: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


    async def _process_video(self, file_id: str) -> None:
        """Process the video in a separate thread."""
        if file_id not in self.video_jobs:
            logger.error(f"Video job not found: {file_id}")
            return
            
        video_info = self.video_jobs[file_id]
        original_video_db_data = await self.original_video_repo.get_by_columns({"video_id": file_id})
        original_video_db_data = original_video_db_data[0]
        updated_info = await self.ffmpeg_service.trim_video(video_info,skip_pairs=[(300, 600), (1200, 1500)])
        self.video_jobs[file_id] = updated_info
        
        for segment in updated_info.segments:
            trimmed_video = TrimmedVideo(
                original_video_id=original_video_db_data.id,
                start_time=timedelta(seconds=0),
                end_time=timedelta(seconds=0),
                remark="",
                description="",
                hashtags=[],
                thumbnail=None,
                file_name=segment,
                location=os.path.join(config.config_properties.UPLOAD_DIR, segment)
            )
            await self.trimmed_video_repo.save(trimmed_video)
    
    def get_video_status(self, file_id: str) -> VideoInfo:
        """Get the status of a video processing job."""
        if file_id not in self.video_jobs:
            raise HTTPException(status_code=404, detail=f"Video job not found: {file_id}")
        return self.video_jobs[file_id]
    
    def get_all_videos(self) -> List[VideoInfo]:
        """Get all video jobs."""
        return list(self.video_jobs.values())

    def shutdown(self):
        """Shutdown the executor properly."""
        self.executor.shutdown(wait=True)

    async def get_all_original_videos(self) -> List[OriginalVideoDTO]:
        """Retrieve all records from the OriginalVideo table."""
        try:
            original_videos = await self.original_video_repo.get_all()
            return [OriginalVideoDTO(**video.__dict__) for video in original_videos]
        except Exception as e:
            logger.error(f"Error retrieving original videos: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to retrieve original videos: {str(e)}")

    async def get_trimmed_videos_by_original_file_id(self, file_id: str) -> List[TrimmedVideoDTO]:
        """Retrieve all trimmed videos for a given original file ID."""
        try:
            original_video_db_data = await self.original_video_repo.get_by_columns({"video_id": file_id})
            original_video_db_data = original_video_db_data[0]
            trimmed_videos = await self.trimmed_video_repo.get_by_columns({"original_video_id": original_video_db_data.id})

            return [TrimmedVideoDTO(**video.__dict__) for video in trimmed_videos]
        except Exception as e:
            logger.error(f"Error retrieving trimmed videos for original file ID {file_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to retrieve trimmed videos: {str(e)}")