from datetime import timedelta, datetime
from typing import Optional, List

from pydantic import BaseModel

class OriginalVideoDTO(BaseModel):
    video_id: str
    name: str
    location: str
    size: int
    video_metadata: dict
    created_user: str
    description: str
    category: str
    remark: str
    addon: dict


class TrimmedVideoDTO(BaseModel):
    original_video_id: int
    start_time: timedelta
    end_time: timedelta
    remark: Optional[str]
    created_time: Optional[datetime]
    updated_time: Optional[datetime]
    description: Optional[str]
    hashtags: Optional[List[str]]
    thumbnail: Optional[bytes]
    file_name: str
    location: str
