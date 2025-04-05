import json
import uuid

from config import constants
from database.database_models import OriginalVideo, TrimmedVideo
from database.repository.original_video_repository import OriginalVideoRepository
from database.repository.trimmed_video_repository import TrimmedVideoRepository
from models.redis_model import TransferDocument, ProcessedDataReceiver
from models.video_models import VideoProcessInfo, VideoUploadResponse, ProcessingStatus
from redis_queue.redis_client import RedisManager
from telegram_bot.messenger import TelegramMessenger


class RedisService:
    def __init__(self):
        self.redis_client = RedisManager.get_client()
        self.original_video_repo = OriginalVideoRepository()
        self.trimmed_video_repo = TrimmedVideoRepository()
        self.telegram_messenger = TelegramMessenger(None, None)

    def upload_to_redis(self, video_process_info: VideoProcessInfo, telegram_chat_id : int):
        if video_process_info and video_process_info.url:
            job_id = str(uuid.uuid4())
            # Save to database
            original_video = OriginalVideo(
                name=video_process_info.file_name,
                video_id=job_id,
                location=video_process_info.url,
                video_metadata={},  # Add any metadata if available
                created_user="system",  # Replace with actual user if available
                description="Original video",
                category="Uncategorized",
                remark="",
                addon={}
            )

            saved_data, video_id = self.original_video_repo.save(original_video)
            transfer_doc = TransferDocument.from_video_process_info(video_process_info, video_id)
            transfer_doc.original_video_id= video_id
            transfer_doc.telegram_chat_id = telegram_chat_id


            # Convert TransferDocument to dictionary before JSON serialization
            transfer_doc_dict = transfer_doc.to_dict() if hasattr(transfer_doc, 'to_dict') else vars(transfer_doc)

            self.redis_client.hset(job_id, mapping={
                "data": json.dumps(transfer_doc_dict),
                "status": ProcessingStatus.PENDING
            })

            self.redis_client.lpush(constants.REDIS_VIDEO_QUEUE_NAME, job_id)
            return VideoUploadResponse(file=video_process_info.url, file_id=job_id, status="pending")

    def get_processed_video_and_upload(self, job_id: str):
        # Get the processed video from Redis
        video_data = self.redis_client.hget(job_id, "data")
        if video_data:
            video_data = json.loads(video_data)
            processed_data = ProcessedDataReceiver.model_validate(video_data)
            db_entity : TrimmedVideo = TrimmedVideo(
                original_video_id=processed_data.original_video_id,
                file_name = processed_data.file_name,
                location = processed_data.location
            )
            self.trimmed_video_repo.save(db_entity)
            if processed_data.telegram_chat_id:
                self.telegram_messenger.send_message_with_chat_id(int(processed_data.telegram_chat_id), processed_data.location)
            return video_data
        else:
            return None
