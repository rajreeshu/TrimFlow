from typing import Optional, List, Tuple

from pydantic import BaseModel

from config import constants
from models.video_models import MediaType, VideoScreenType, VideoProcessInfo


class TransferDocument(BaseModel):
    media_type: Optional[MediaType] = None
    url: Optional[str] = None
    file_name: Optional[str] = None
    segment_time: Optional[int] = None
    start_time: Optional[int] = None
    end_time: Optional[int] = None
    skip_pairs: Optional[List[Tuple[int, int]]] = None
    screen_type: Optional[VideoScreenType] = None
    edit_type: Optional[str] = None
    original_video_id: Optional[str] = None
    telegram_chat_id : Optional[int] = None

    @classmethod
    def from_video_process_info(cls, video_process_info: 'VideoProcessInfo',
                                original_id: Optional[str] = None) -> 'TransferDocument':
        doc = cls()
        process_data = video_process_info.model_dump()

        # Copy all matching attributes
        for attr in process_data:
            if hasattr(doc, attr):
                setattr(doc, attr, process_data[attr])

        doc.original_video_id = original_id
        return doc

class ProcessedDataReceiver(BaseModel):
    original_video_id: Optional[int] = None
    file_name : Optional[str] = None
    location: Optional[str] = None
    telegram_chat_id: Optional[int|str] = None