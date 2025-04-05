import redis
from fastapi import HTTPException

from controllers.video_controller_interface import UploadControllerInterface
from models.file_type_model import FileData
from models.video_models import VideoProcessInfo
from services.redis_service import RedisService


class UrlController(UploadControllerInterface):
    def __init__(self):
        self.redis_service = RedisService()


    def upload(self, video_process_info: VideoProcessInfo, file_data: FileData, telegram_chat_id: int):
        if not file_data or not video_process_info:
            raise HTTPException(status_code=400, detail="Missing required Fields")
        video_process_info.url= file_data.url
        # Upload to Redis
        return self.redis_service.upload_to_redis(video_process_info, telegram_chat_id)


