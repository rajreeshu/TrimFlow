from enum import Enum
from typing import Optional, List, Tuple

from pydantic import BaseModel

import config.constants as constants


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class VideoUploadResponse(BaseModel):
    file: str
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

class VideoScreenType(str,Enum):
    LANDSCAPE = "landscape"
    PORTRAIT = "portrait"

class VideoEditType(str, Enum):
    GAME_PLAY = "game_play"
    STATIC_COLOR = "static_color"

class MediaType(str, Enum):
    VIDEO = constants.VIDEO
    IMAGE = constants.IMAGE

class VideoProcessInfo(BaseModel):
    media_type: Optional[MediaType] = MediaType.VIDEO
    url: Optional[str]=None
    file_name : Optional[str] = None
    segment_time: int = constants.DEFAULT_VIDEO_SEGMENT_TIME
    start_time: int = constants.DEFAULT_START_TIME
    end_time: int = constants.DEFAULT_END_TIME
    skip_pairs: List[Tuple[int, int]] = []
    screen_type: VideoScreenType = VideoScreenType.LANDSCAPE
    edit_type: Optional[str] = None  # To be done

