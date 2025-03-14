from pydantic import BaseModel
from enum import Enum
from typing import Optional, List

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