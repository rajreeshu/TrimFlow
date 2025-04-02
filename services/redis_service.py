import json
import uuid

from config import constants
from models.video_models import VideoProcessInfo, VideoUploadResponse


class RedisService:
    def __init__(self, redis_client):
        self.redis_client = redis_client

    def upload_to_redis(self, video_process_info: VideoProcessInfo):
        if video_process_info and video_process_info.url:

            job_id = str(uuid.uuid4())
            self.redis_client.hset(job_id, mapping={
                "data": json.dumps(video_process_info.model_dump()),
                "status": "pending"
            })

            self.redis_client.lpush(constants.REDIS_VIDEO_QUEUE_NAME, job_id)
            return VideoUploadResponse(file=video_process_info.url, file_id=job_id, status="pending")