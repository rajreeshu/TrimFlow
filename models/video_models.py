from symtable import Class

from pydantic import BaseModel
from enum import Enum
from typing import Optional, List, Tuple


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class VideoUploadResponse(BaseModel):
    """Response for video upload."""
    filename: str
    file_id: str
    job_id: Optional[str] = None
    status: str
    message: str

class VideoInfo(BaseModel):
    file_id: str
    filename: str
    original_path: str
    status: ProcessingStatus
    segments: List[str] = []
    error: Optional[str] = None

class VideoScreenType(Enum):
    LANDSCAPE = "landscape"
    PORTRAIT = "portrait"

class VideoEditType(Enum):
    GAME_PLAY = "game_play"
    STATIC_COLOR = "static_color"

class VideoProcessInfo(BaseModel):
    segment_time: Optional[int] = None
    skip_pairs: Optional[List[Tuple[int, int]]] = None
    screen_type: Optional[VideoScreenType] = None
    edit_type: Optional[str] = None
    start_time: Optional[int] = None
    end_time: Optional[int] = None

class VideoJobInfo(BaseModel):
    """Information about a video processing job in the queue."""
    file_id: str
    job_id: str
    video_info: VideoInfo
