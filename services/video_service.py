from concurrent.futures import ThreadPoolExecutor
import os
from fastapi import UploadFile, HTTPException
import logging
import asyncio
from datetime import timedelta
from typing import Dict, List
from telegram import Update
from telegram.ext import CallbackContext

from database.database_dto import OriginalVideoDTO, TrimmedVideoDTO
from database.repository.original_video_repository import OriginalVideoRepository
from database.repository.trimmed_video_repository import TrimmedVideoRepository
from models.video_models import VideoInfo, ProcessingStatus, VideoProcessInfo, VideoJobInfo
import utils.file_utils as file_utils
import utils.validators as validators
from database.database_models import OriginalVideo, TrimmedVideo
import services.subtitle_service as subtitle_service
from services.ffmpeg_service import FfmpegService
from services.queue_service import enqueue_video_processing, get_job_status
from config.config import config_properties
import urllib.parse

from telegram_bot.messenger import TelegramMessenger

logger = logging.getLogger(__name__)

class VideoService:
    def __init__(self, ffmpeg_service: FfmpegService, update: Update, context: CallbackContext):
        self.executor = ThreadPoolExecutor(max_workers=config_properties.MAX_WORKERS)
        self.video_jobs: Dict[str, VideoJobInfo] = {}
        self.ffmpeg_service = ffmpeg_service
        self.original_video_repo = OriginalVideoRepository()
        self.trimmed_video_repo = TrimmedVideoRepository()
        self.telegram_messenger = TelegramMessenger(update, context)
        self.chat_id = update.effective_chat.id if update and hasattr(update, 'effective_chat') else None

    async def upload_and_process(self, file: UploadFile, video_process_info: VideoProcessInfo) -> VideoJobInfo:
        """Upload a video file and submit for processing."""
        try:
            # Validate file
            validators.validate_video_file(file.filename)
            
            # Generate unique filename and ID
            unique_filename, file_id = validators.generate_unique_filename(file.filename)

            # Save video file
            file_path = os.path.join(config_properties.UPLOAD_DIR, unique_filename)
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
            if video_process_info.start_time is None:
                video_process_info.start_time = subtitle_service.find_movie_start_time(file_path)

            # Remove metadata from the video file
            cleaned_file_path = self.ffmpeg_service.remove_metadata(file_path)

            # Create video info object
            video_info = VideoInfo(
                file_id=file_id,
                filename=unique_filename,
                original_path=cleaned_file_path,
                status=ProcessingStatus.PENDING
            )

            # Enqueue the job
            job_id = enqueue_video_processing(video_info, video_process_info, self.chat_id)
            
            # Create and store job info
            job_info = VideoJobInfo(
                file_id=file_id,
                job_id=job_id,
                video_info=video_info
            )
            self.video_jobs[file_id] = job_info
            
            return job_info

        except Exception as e:
            logger.error(f"Error processing upload: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    
    def get_video_status(self, file_id: str) -> VideoJobInfo:
        """Get the status of a video processing job."""
        if file_id not in self.video_jobs:
            raise HTTPException(status_code=404, detail=f"Video job not found: {file_id}")
        
        job_info = self.video_jobs[file_id]
        
        # If job_id is a fallback ID (Redis wasn't available), skip queue status check
        if job_info.job_id in ["no_queue_fallback", "exception_fallback"]:
            job_info.video_info.status = ProcessingStatus.COMPLETED
            return job_info
            
        # Get latest status from queue
        job_status = get_job_status(job_info.job_id)
        
        # Update job status
        if job_status['status'] == 'finished' and job_status['result']:
            # Update VideoInfo with result
            job_info.video_info = VideoInfo(**job_status['result'])
        elif job_status['status'] == 'failed':
            job_info.video_info.status = ProcessingStatus.FAILED
            job_info.video_info.error = "Job failed in queue"
        elif job_status['status'] == 'error':
            # Handle error with Redis connection
            job_info.video_info.status = ProcessingStatus.FAILED
            job_info.video_info.error = job_status.get('message', 'Error with queue service')
        elif job_status['status'] == 'fallback_completed':
            job_info.video_info.status = ProcessingStatus.COMPLETED
        
        return job_info
    
    def get_all_videos(self) -> List[VideoJobInfo]:
        """Get all video jobs."""
        return list(self.video_jobs.values())

    def shutdown(self):
        """Shutdown the executor properly."""
        self.executor.shutdown(wait=True)

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