from concurrent.futures import ThreadPoolExecutor
import os
from fastapi import UploadFile, HTTPException
import logging
from typing import Dict, List
from fastapi import Depends

from models.video_models import VideoInfo, ProcessingStatus
from utils.file_utils import save_file_in_chunks
from utils.validators import validate_video_file, generate_unique_filename
from services.ffmpeg_service import trim_video
from config.config import settings
from utils.database_utils import save_original_video
from models.database_models import OriginalVideo
from services.subtitle_service import find_movie_start_time, get_subtitle_from_video

import subprocess

logger = logging.getLogger(__name__)

class VideoService:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=settings.MAX_WORKERS)
        self.video_jobs: Dict[str, VideoInfo] = {}
        
    async def upload_and_process(self, file: UploadFile) -> VideoInfo:
        """Upload a video file and submit for processing."""
        try:
            # Validate file
            validate_video_file(file.filename)
            
            # Generate unique filename and ID
            unique_filename, file_id = generate_unique_filename(file.filename)
            file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
            
            # Create video info object
            video_info = VideoInfo(
                file_id=file_id,
                filename=unique_filename,
                original_path=file_path,
                status=ProcessingStatus.PENDING
            )

            # Save video file
            await save_file_in_chunks(file, file_path)

            movie_start_time = find_movie_start_time(file_path)

             # Remove metadata from the video file
            cleaned_file_path = self.remove_metadata(file_path)
            video_info.original_path = cleaned_file_path

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

            await save_original_video(original_video)

            start_time = find_movie_start_time(file.filename)
            
            # Submit for processing
            self.video_jobs[file_id] = video_info
            self.executor.submit(self._process_video, file_id)
            
            return video_info
            
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Error processing upload: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    
    def remove_metadata(self, file_path: str) -> str:
        """Remove all metadata from the video file."""
        base, ext = os.path.splitext(file_path)
        cleaned_file_path = f"{base}_cleaned{ext}"
        command = [
            "ffmpeg",
            "-i", file_path,
            "-map", "0:v",  # Map only the video stream
            "-map", "0:a",  # Map only the audio stream
            "-c", "copy",
            "-map_metadata", "-1",  # Remove all metadata
            cleaned_file_path
        ]
        
        try:
            logger.info(f"Removing metadata from {file_path}")
            subprocess.run(command, check=True)
            logger.info(f"Metadata removed, saved to {cleaned_file_path}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error removing metadata from {file_path}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to remove metadata: {str(e)}")
        
        return cleaned_file_path


    def _process_video(self, file_id: str) -> None:
        """Process the video in a separate thread."""
        if file_id not in self.video_jobs:
            logger.error(f"Video job not found: {file_id}")
            return
            
        video_info = self.video_jobs[file_id]
        updated_info = trim_video(video_info)
        self.video_jobs[file_id] = updated_info
    
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
