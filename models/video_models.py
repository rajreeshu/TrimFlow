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
    filename: str
    file_id: str
    status: str
    message: Optional[str] = None

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
