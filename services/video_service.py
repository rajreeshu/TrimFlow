from concurrent.futures import ThreadPoolExecutor
import os
from fastapi import UploadFile, HTTPException
import logging
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from models.video_models import VideoInfo, ProcessingStatus
from utils.file_utils import save_file_in_chunks
from utils.validators import validate_video_file, generate_unique_filename
from actions.ffmpeg_action import trim_video
from config.config import settings
from utils.database_utils import save_original_video, get_db
from models.database_models import OriginalVideo

logger = logging.getLogger(__name__)

class VideoService:
    def __init__(self, db: Optional[AsyncSession] = None):
        self.executor = ThreadPoolExecutor(max_workers=settings.MAX_WORKERS)
        self.video_jobs: Dict[str, VideoInfo] = {}
        self.db = db
        
    async def upload_and_process(self, file: UploadFile,  db: AsyncSession = None) -> VideoInfo:
        """Upload a video file and submit for processing."""
        db_session = db or self.db
        if not db_session:
            raise ValueError("Database session is required")
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

            await save_original_video(original_video, db_session)
            
            # Submit for processing
            self.video_jobs[file_id] = video_info
            self.executor.submit(self._process_video, file_id)
            
            return video_info
            
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Error processing upload: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    
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
